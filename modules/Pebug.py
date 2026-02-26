#!/usr/bin/env python3
"""
pebug (class-based) - x86 DOS-debug-inspired debugger core
Autor: Pablo Niklas
Refactor OO: integración con TUI/WEB/GUI
"""

import os
import re
import readline
import sys
import random
from enum import Enum

# Dependencias del proyecto
from modules.Disk import Disk
from modules.Memory import Memory
from modules.CpuX8086 import CpuX8086
from modules.Terminal import Terminal, AnsiColors


import io
from contextlib import redirect_stdout, redirect_stderr


class Pebug:
    """
    Núcleo de Pebug encapsulado en una clase, apto para integraciones con otras interfaces.

    - Inyectá un Terminal (o tu adaptador) en el constructor.
    - Llamá a `start()` para inicializar (banner, carga de disco, etc.).
    - Usá `execute_line(cmd)` para procesar una línea de comando (ideal UIs).
    - `run()` ofrece el loop interactivo clásico (CLI).
    - `cleanup()` guarda el estado del disco en salida limpia.
    """

    class Mode(Enum):
        COMMAND = "🅒 "
        ASSEMBLE = "🅐 "

    # ====== Inicialización / ciclo de vida ======
    def __init__(
        self,
        terminal: Terminal,
        filename: str = "pebug_disk.bin",
        memory_pages: int = 10,    # 640KB si 1 página = 64KB
        disk_size: int = 65536,    # 64KB
        cpu: CpuX8086 | None = None,
        memory: Memory | None = None,
        disk: Disk | None = None,
    ):
        self.terminal = terminal
        self.memory = memory or Memory(memory_pages)
        self.disk = disk or Disk(disk_size, filename)
        self.cpu = cpu or CpuX8086()

        # Estado
        self.mode = self.Mode.COMMAND
        self.running = False

        # Ajustes iniciales CPU
        self.cpu.instruction_parser.register_collection.set('SP', 0xFFFE)

        # Compilación de patrones → handlers
        H4 = r"[0-9a-fA-F]{1,4}"
        H2 = r"[0-9a-fA-F]{1,2}"
        self._handlers = [
            (re.compile(
                r"^[sS]\s+([0-9a-fA-F]{0,4})\s+(.+)$"), self._cmd_search),
            (re.compile(r"^[hH]\s+(" + H4 +
             r")\s+(" + H4 + r")$"), self._cmd_hex),
            (re.compile(r"^[rR]$"), self._cmd_regs),
            (re.compile(r"^[cC]\s+(" + H4 + r")\s+(" + H4 +
             r")\s+(" + H4 + r")$"), self._cmd_compare),
            (re.compile(r"^[cC][aA][tT]\s+(" + H4 +
             r")\s+(" + H4 + r")$"), self._cmd_cat),
            (re.compile(r"^[mM]\s+(" + H4 + r")\s+(" +
             H4 + r")\s+(" + H4 + r")$"), self._cmd_move),
            (re.compile(r"^[oO][vV]$"), lambda *_: setattr(self.cpu,
             "OF", 0b1) or self._ok("OF=1")),
            (re.compile(r"^[nN][vV]$"), lambda *_: setattr(self.cpu,
             "OF", 0b0) or self._ok("OF=0")),
            (re.compile(r"^[nN][gG]$"), lambda *_: setattr(self.cpu,
             "SF", 0b1) or self._ok("SF=1")),
            (re.compile(r"^[pP][lL]$"), lambda *_: setattr(self.cpu,
             "sh", 0b0) or self._ok("SH=0")),
            (re.compile(r"^[zZ][rR]$"), lambda *_: setattr(self.cpu,
             "ZF", 0b1) or self._ok("ZF=1")),
            (re.compile(r"^[nN][zZ]$"), lambda *_: setattr(self.cpu,
             "ZF", 0b0) or self._ok("ZF=0")),
            (re.compile(r"^[aA][cC]$"), lambda *_: setattr(self.cpu,
             "AC", 0b1) or self._ok("AC=1")),
            (re.compile(r"^[nN][aA]$"), lambda *_: setattr(self.cpu,
             "AC", 0b0) or self._ok("AC=0")),
            (re.compile(r"^[pP][eE]$"), lambda *_: setattr(self.cpu,
             "OP", 0b1) or self._ok("OP=1")),
            (re.compile(r"^[pP][oO]$"), lambda *_: setattr(self.cpu,
             "OP", 0b0) or self._ok("OP=0")),
            (re.compile(r"^[cC][yY]$"), lambda *_: setattr(self.cpu,
             "CY", 0b1) or self._ok("CY=1")),
            (re.compile(r"^[nN][cC]$"), lambda *_: setattr(self.cpu,
             "CY", 0b0) or self._ok("CY=0")),
            (re.compile(r"^[fF]\s+(" + H4 + r")\s+(" + H4 + r")$"),
             self._cmd_reset_range),
            (re.compile(r"^[fF]\s+(" + H4 + r")\s+(" +
             H4 + r")\s+(.+)$"), self._cmd_fill_range),
            (re.compile(r"^[dD]\s+(" + H4 + r")\s+(" + H4 + r")$"),
             self._cmd_display),
            (re.compile(r"^[sS][pP]\s+(" + H4 + r")$"), self._cmd_set_page),
            (re.compile(r"^[eE]\s+(" + H4 + r")\s+(" + H2 + r")$"),
             self._cmd_byte_poke),
            (re.compile(r"^[eE]\s+(" + H4 + r")\s+\'(.*)\'$"),
             self._cmd_string_poke),
            (re.compile(r"^[dD][eE][mM][oO]$"), self._cmd_demo),
            (re.compile(r"^[wW]\s+(" + H4 + r")\s+(" +
             H4 + r")\s+(" + H4 + r")$"), self._cmd_write),
            (re.compile(r"^[lL]\s+(" + H4 + r")\s+(" +
             H4 + r")\s+(" + H4 + r")$"), self._cmd_read),
            (re.compile(r"^[pP]\s+(.+)$"), self._cmd_parse),
            (re.compile(r"^[tT](?:\s+(on|off|clear))?$"), self._cmd_trace),
            (re.compile(r"^[bB](?:\s+.*)?$"), self._cmd_breakpoint),
            (re.compile(r"^[vV](?:\s+.*)?$"), self._cmd_watch),
            (re.compile(r"^[nN]$"), self._cmd_step),
            (re.compile(r"^[gG]$"), self._cmd_cont),
            (re.compile(
                r"^[uU](?:\s+([0-9a-fA-F]{1,4})(?:\s+(\d+))?)?$"), self._cmd_disassemble),
        ]

    def start(self, show_banner: bool = True):
        """Inicializa entorno: carga disco, muestra banner por Terminal, etc."""
        self.disk.load()
        if show_banner:
            self._banner()   # ahora va por terminal.*
        self._hello()
        self.running = True

    def cleanup(self):
        """Guarda el estado del disco y emite despedida."""
        self.disk.save()
        self.terminal.info_message("Bye! =)")
        self.terminal.success_message("✔")

    # ====== REPL clásico (opcional) ======
    def run(self):
        """Loop interactivo clásico (ideal para CLI)."""
        self.start()

        # Historial de readline (solo CLI)
        histfile = os.path.join(os.path.expanduser("~"), ".pebughist")
        try:
            readline.read_history_file(histfile)
            readline.set_history_length(1000)
        except IOError:
            pass

        # Primer prompt
        try:
            cmd = self._prompt(self.mode.value)
        except (KeyboardInterrupt, EOFError):
            cmd = "q"

        while not re.match(r"^[qQ]", cmd or "") and self.running:
            self.execute_line(cmd)
            try:
                cmd = self._prompt(self.mode.value)
            except (KeyboardInterrupt, EOFError):
                cmd = "q"

        self.cleanup()
        readline.write_history_file(histfile)
        sys.exit(0)

    # ====== API principal para UIs ======
    def execute_line(self, cmd: str) -> dict:
        """
        Procesa una única línea de comando.
        Retorna un dict con info básica útil para UIs.
        """
        if cmd is None:
            return {"handled": False, "exit": False, "mode": self.mode.name}

        # Salir global desde cualquier modo
        if re.match(r"^[qQ]$", cmd.strip()):
            if self.mode == self.Mode.ASSEMBLE:
                # salir del modo assemble → volver a COMMAND
                self.mode = self.Mode.COMMAND
                self.terminal.info_message(
                    "Assemble: quit → back to COMMAND mode.")
                return {"handled": True, "exit": False, "mode": self.mode.name}
            # salir del programa
            self.running = False
            self.cleanup()
            return {"handled": True, "exit": True, "mode": self.mode.name}

        # Si estamos en modo ASSEMBLE y no es 'q', tratamos la línea como ensamblado
        if self.mode == self.Mode.ASSEMBLE:
            return self._assemble_line(cmd)

        # Comando 'a' → entrar a modo assemble
        if re.match(r"^[aA]$", cmd.strip()):
            self.mode = self.Mode.ASSEMBLE
            self.terminal.info_message(
                "Bienvenido al modo Assemble. Escribí 'q' para salir.")
            self.terminal.info_message(
                "Usá números en Hex (0x), Decimal o Binario (0b).")
            self._show_asm_prompt()
            return {"handled": True, "exit": False, "mode": self.mode.name}

        # Despacho por patrones
        for rx, handler in self._handlers:
            m = rx.match(cmd.strip())
            if m:
                try:
                    handler(*m.groups())
                except Exception as ex:
                    self.terminal.error_message(f"ERROR: {ex}")
                return {"handled": True, "exit": False, "mode": self.mode.name}

        # Si nada matcheó:
        self._error_msg()
        return {"handled": False, "exit": False, "mode": self.mode.name}

    # ====== Helpers UI / Prompt ======
    def get_prompt(self) -> str:
        return self.mode.value + " •❯ "

    def _prompt(self, mode: str = "") -> str:
        return input(f"{mode}{AnsiColors.BRIGHT_GREEN.value}•❯{AnsiColors.RESET.value} ")

    def _show_asm_prompt(self):
        self.terminal.info_message(
            f"Cursor @ {self.memory.active_page:04X}:{self.memory.offset_cursor:04X}"
        )

    # ====== Mensajería ======
    def _error_msg(self):
        self.terminal.error_message("Input no reconocido.")

    def _ok(self, msg="OK"):
        self.terminal.success_message(msg)

    # ====== Banner / Hello ======
    def _banner(self):
        art = (
            "░       ░░░        ░░       ░░░  ░░░░  ░░░      ░░\n"
            "▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒\n"
            "▓       ▓▓▓      ▓▓▓▓       ▓▓▓  ▓▓▓▓  ▓▓  ▓▓▓   ▓\n"
            "█  ████████  ████████  ████  ██  ████  ██  ████  █\n"
            "█  ████████        ██       ████      ████      ██"
        )
        self._emit_lines(
            f"{AnsiColors.BRIGHT_YELLOW.value}{art}{AnsiColors.RESET.value}")
        self._emit_lines(
            f"{AnsiColors.BRIGHT_GREEN.value}v1.1{AnsiColors.RESET.value}")

    def _hello(self):
        self.terminal.info_message(
            "An x86 DOS-debug-inspired program written in Python.")
        self.terminal.info_message(
            f"By {AnsiColors.BRIGHT_CYAN.value}Pablo Niklas <pablo.niklas@gmail.com>.{AnsiColors.RESET.value}"
        )
        self.terminal.info_message(
            f"Online manual at {AnsiColors.BRIGHT_BLUE.value}https://pebug.readthedocs.io{AnsiColors.RESET.value}"
        )
        self.terminal.info_message(
            f"History file: {AnsiColors.BRIGHT_YELLOW.value}{readline.get_history_length()} lines loaded.{AnsiColors.RESET.value}"
        )
        self.terminal.info_message(
            f"Main memory size: {AnsiColors.BRIGHT_YELLOW.value}{self.memory.pages} pages.{AnsiColors.RESET.value}"
        )
        self.terminal.info_message(
            f"Stack @ {AnsiColors.BRIGHT_YELLOW.value}{self.cpu.get_hex(self.cpu.instruction_parser.register_collection.get('SP'))}.{AnsiColors.RESET.value}"
        )
        self.terminal.info_message(
            f"Virtual disk size: {AnsiColors.BRIGHT_YELLOW.value}{self.disk.get_size()} bytes.{AnsiColors.RESET.value}"
        )
        self.terminal.info_message(
            f"Supported instructions: {AnsiColors.BRIGHT_MAGENTA.value}{len(self.cpu.instructions_set)} "
            f"{AnsiColors.WHITE.value}({', '.join(sorted(self.cpu.instructions_set))}){AnsiColors.RESET.value}"
        )
        self.terminal.info_message(
            f"Supported registers: {AnsiColors.BRIGHT_GREEN.value}{len(self.cpu.register_set)} "
            f"{AnsiColors.WHITE.value}({', '.join(sorted(self.cpu.register_set))}){AnsiColors.RESET.value}"
        )
        self.terminal.info_message("Type 'q' to quit the program.\033[0m")

    # ====== Mensajería / util stdout→Terminal ======

    def _emit_lines(self, text: str, level: str = "info"):
        if not text:
            return
        emitter = getattr(
            self.terminal, f"{level}_message", self.terminal.info_message)
        for ln in text.splitlines():
            emitter(ln)

    def _forward_stdout(self, fn, *args, level: str = "info"):
        """
        Ejecuta una función que imprime a stdout/stderr y reenvía esas líneas al Terminal.
        Útil para CPU.* que no aceptan callback.
        """
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            fn(*args)
        self._emit_lines(buf.getvalue(), level=level)

    # ====== Implementación de comandos ======

    def _cmd_hex(self, a: str, b: str):
        oper1 = int(a, 16)
        oper2 = int(b, 16)
        res_add = oper1 + oper2
        res_sub = oper1 - oper2
        self.terminal.info_message(f"{res_add:04X}")
        self.terminal.warning_message(f"{res_sub:04X}")

    def _cmd_regs(self):
        self.cpu.print_registers()

    def _cmd_compare(self, a: str, b: str, c: str):
        oper1 = int(a, 16)
        oper2 = int(b, 16)
        oper3 = int(c, 16)
        diff_list = self.cpu.compare(self.memory, oper1, oper2, oper3)
        for aa in diff_list:
            self.terminal.info_message(aa)

    def _cmd_cat(self, a: str, b: str):
        self.cpu.cat(self.disk, int(a, 16), int(b, 16))

    def _cmd_move(self, a: str, b: str, c: str):
        self.cpu.move(self.memory, int(a, 16), int(b, 16), int(c, 16))

    def _cmd_reset_range(self, start: str, end: str):
        self.cpu.fill(self.memory, int(start, 16), int(end, 16), chr(0))

    def _cmd_fill_range(self, start: str, end: str, pattern: str):
        self.cpu.fill(self.memory, int(start, 16), int(end, 16), pattern)

    def _cmd_display(self, a: str, b: str):
        self.cpu.display(self.memory, int(a, 16), int(b, 16))

    def _cmd_set_page(self, page: str):
        self.memory.active_page = int(page, 16)
        self._ok(f"Active page = {self.memory.active_page:04X}")

    def _cmd_byte_poke(self, addr: str, value: str):
        # FIX: orden correcto poke(page, offset, value)
        address = int(addr, 16)
        val = int(value, 16)
        self.memory.poke(self.memory.active_page, address, val)

    def _cmd_string_poke(self, addr: str, text: str):
        self.cpu.load_into(self.memory, int(addr, 16), text)

    def _cmd_demo(self):
        def fortune_cookie():
            fortunes = [
                "You will find great success in your future endeavors.",
                "An unexpected opportunity will bring you joy.",
                "New adventures are on the horizon.",
                "Good things are coming your way.",
                "Happiness is not a destination, it's a way of life.",
                "Today is a good day to be kind to yourself.",
                "You will achieve your goals with patience and persistence.",
                "Someone close to you has an important message for you.",
                "A small act of kindness will bring great joy.",
                "Your creativity will lead you to wonderful places.",
            ]
            return random.choice(fortunes)

        self.cpu.load_into(self.memory, 0, fortune_cookie())
        self.terminal.success_message(
            f"The demo text was loaded into {self.memory.active_page}:0000, enter 'd 0 60' to read it."
        )

    def _cmd_write(self, addr: str, first: str, num: str):
        self.cpu.write_to_vdisk(
            self.memory, self.disk, int(addr, 16), int(first, 16), int(num, 16)
        )

    def _cmd_read(self, addr: str, first: str, num: str):
        self.cpu.read_from_vdisk(
            self.memory, self.disk, int(addr, 16), int(first, 16), int(num, 16)
        )

    def _cmd_parse(self, line: str):
        self.cpu.parse_instruction(line, self.memory)

    def _cmd_search(self, start: str, pattern: str):
        st = int(start, 16) if start else 0
        found_list = self.cpu.search(self.memory, st, pattern)
        for aa in found_list:
            self.terminal.info_message(aa)

    # ---- Trace / Breakpoints / Watches / Step / Cont / Disas ----
    def _cmd_trace(self, arg: str | None):
        ip = self.cpu.instruction_parser
        if not hasattr(ip, "enable_trace"):
            self.terminal.error_message("Trace API no disponible.")
            return
        if arg is None:
            state = getattr(ip, "trace_enabled", False)
            self.terminal.info_message(f"Trace is {'ON' if state else 'OFF'}")
            return
        arg = arg.lower()
        if arg == "on":
            ip.enable_trace(True, out=lambda s: self.terminal.info_message(s))
            self.terminal.success_message("Trace ON")
        elif arg == "off":
            ip.enable_trace(False)
            self.terminal.success_message("Trace OFF")
        elif arg == "clear":
            clear_fn = getattr(ip, "clear_trace_buffer", None)
            if callable(clear_fn):
                clear_fn()
                self.terminal.success_message("Trace buffer cleared")
            else:
                ip.enable_trace(False)
                ip.enable_trace(
                    True, out=lambda s: self.terminal.info_message(s))
                self.terminal.warning_message(
                    "Trace buffer: reset via OFF/ON (no clear API)")
        else:
            self.terminal.error_message("Uso: t [on|off|clear]")

    def _cmd_breakpoint(self, cmd: str):
        ip = self.cpu.instruction_parser
        parts = cmd.strip().split(maxsplit=2)
        if len(parts) == 1:
            lst = getattr(ip, "list_breakpoints", None)
            if callable(lst):
                bps = lst()
                if not bps:
                    self.terminal.info_message("(no breakpoints)")
                else:
                    for b in bps:
                        self.terminal.info_message(f"bp: {b}")
            else:
                self.terminal.warning_message("No list_breakpoints API.")
            return
        if len(parts) >= 2 and parts[1] == "-":
            if len(parts) == 3:
                rem = getattr(ip, "remove_breakpoint", None)
                if callable(rem):
                    rem(parts[2])
                    self.terminal.success_message(
                        f"Breakpoint removed: {parts[2]}")
                    return
                self.terminal.error_message(
                    "remove_breakpoint API no disponible.")
                return
            self.terminal.error_message("Uso: b - <label|addr>")
            return
        add = getattr(ip, "add_breakpoint", None)
        if callable(add):
            add(parts[1])
            self.terminal.success_message(f"Breakpoint added: {parts[1]}")
        else:
            self.terminal.error_message("add_breakpoint API no disponible.")

    def _cmd_watch(self, cmd: str):
        ip = self.cpu.instruction_parser
        parts = cmd.strip().split(maxsplit=2)
        if len(parts) == 1:
            getw = getattr(ip, "list_watches", None)
            if callable(getw):
                ws = getw()
                if not ws:
                    self.terminal.info_message("(no watches)")
                else:
                    for w in ws:
                        self.terminal.info_message(f"watch: {w}")
            else:
                self.terminal.warning_message("No list_watches API.")
            return
        if parts[1].lower() == "clear":
            clr = getattr(ip, "clear_watches", None)
            if callable(clr):
                clr()
                self.terminal.success_message("Watches cleared")
            else:
                self.terminal.error_message("clear_watches API no disponible.")
            return
        if parts[1] == "-":
            if len(parts) == 3:
                rm = getattr(ip, "remove_watch", None)
                if callable(rm):
                    rm(parts[2])
                    self.terminal.success_message(f"Watch removed: {parts[2]}")
                    return
                self.terminal.error_message("remove_watch API no disponible.")
                return
            self.terminal.error_message("Uso: v - <what>")
            return
        addw = getattr(ip, "add_watch", None)
        if callable(addw):
            addw(" ".join(parts[1:]))
            self.terminal.success_message(
                f"Watch added: {' '.join(parts[1:])}")
        else:
            self.terminal.error_message("add_watch API no disponible.")

    def _cmd_step(self):
        ip = self.cpu.instruction_parser
        fn = getattr(ip, "step", None)
        if not callable(fn):
            self.terminal.error_message("step API no disponible.")
            return
        try:
            fn(self.memory)
            self.terminal.info_message("STEP")
        except Exception as ex:
            self.terminal.error_message(f"STEP error: {ex}")

    def _cmd_cont(self):
        ip = self.cpu.instruction_parser
        fn = getattr(ip, "cont", None)
        if not callable(fn):
            self.terminal.error_message("cont API no disponible.")
            return
        try:
            fn(self.memory)
            self.terminal.info_message("CONT finished")
        except Exception as ex:
            self.terminal.error_message(f"CONT error: {ex}")

    def _cmd_disassemble(self, start: str | None, count: str | None):
        ip = self.cpu.instruction_parser
        s = self.memory.offset_cursor if not start else int(start, 16)
        c = 8 if not count else int(count)
        fn1 = getattr(ip, "disassemble_from_memory", None)
        fn2 = getattr(ip, "disassemble_program", None)
        try:
            if callable(fn1):
                lines = fn1(self.memory, s, c)
            elif callable(fn2):
                lines = fn2(self.memory, s, c)
            else:
                self.terminal.error_message("Disassembler API no disponible.")
                return
            for ln in lines:
                self.terminal.info_message(ln)
        except Exception as ex:
            self.terminal.error_message(f"DISAS error: {ex}")

    # ====== Assemble Mode (stateful) ======
    def _assemble_line(self, line: str) -> dict:
        """Procesa una línea en modo ASSEMBLE."""
        ip = self.cpu.instruction_parser
        try:
            if not hasattr(ip, "assemble_line"):
                raise RuntimeError("assemble_line API no disponible")
            bytes_seq = ip.assemble_line(line) or []
            for mc in bytes_seq:
                self.memory.poke(self.memory.active_page,
                                 self.memory.offset_cursor, mc)
                self.memory.offset_cursor += 1
            self._show_asm_prompt()
            return {"handled": True, "exit": False, "mode": self.mode.name}
        except Exception as ex:
            self.terminal.error_message(f"ASSEMBLE ERROR: {ex}")
            self._show_asm_prompt()
            return {"handled": False, "exit": False, "mode": self.mode.name}

def pebug_main(terminal: Terminal, filename: str = "pebug_disk.bin"):
    """
    Punto de entrada legacy usado por tests (p.ej., tests/test_cli_commands.py).
    Crea una instancia de Pebug y corre un bucle que lee de input() (pytest lo monkeypatchea).
    No hace sys.exit().
    """
    app = Pebug(terminal=terminal, filename=filename)
    app.start()

    # Bucle de lectura por consola
    while app.running:
        try:
            cmd = input(app.get_prompt())
        except (KeyboardInterrupt, EOFError):
            cmd = "q"

        res = app.execute_line(cmd)
        if res.get("exit"):
            break

    # Si quedó corriendo (por EOF/KeyboardInterrupt), cerramos prolijo
    if app.running:
        app.cleanup()


# ====== Runner opcional cuando se ejecuta como script ======
if __name__ == "__main__":
    term = Terminal()
    pebug_main(term)