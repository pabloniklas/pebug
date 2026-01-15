from typing import (
    List,
    Dict,
    Tuple,
    Optional
)

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Callable, Any

import re

from multipledispatch import dispatch

from rply import (
    ParserGenerator,
    LexerGenerator
)

from enum import Enum

if __name__ is not None and "." in __name__:
    from .Memory import Memory
    from .Disk import Disk
    from .Terminal import Terminal, AnsiColors
else:
    from Memory import Memory
    from Disk import Disk
    from Terminal import Terminal, AnsiColors

# https://joshsharp.com.au/blog/rpython-rply-interpreter-1.html


@dataclass
class TraceRecord:
    opcode: str
    operands: List[str]
    pseudo_bytes: Optional[List[int]] = None
    regs_before: Dict[str, int] = field(default_factory=dict)
    regs_after: Dict[str, int] = field(default_factory=dict)
    flags_before: Dict[str, int] = field(default_factory=dict)
    flags_after: Dict[str, int] = field(default_factory=dict)
    mem_accesses: List[Tuple[str, int, int, int]] = field(
        default_factory=list)  # ('R'|'W', page, addr, val)


class TracedMemory:
    """
    Envueltura de Memory que registra accesos R/W para la traza.
    """

    def __init__(self, base_memory):
        self._m = base_memory
        self.accesses: List[Tuple[str, int, int, int]] = []

    # Passthrough a atributos (active_page, etc.)
    def __getattr__(self, name):
        return getattr(self._m, name)

    def peek(self, page: int, addr: int) -> int:
        v = self._m.peek(page, addr)
        self.accesses.append(('R', page, addr, v))
        return v

    def poke(self, page: int, addr: int, val: int) -> None:
        self._m.poke(page, addr, val)
        self.accesses.append(('W', page, addr, val))


class Icons(Enum):
    """Icons used in the terminal interface."""
    MACHINE_CODE: str = "🖥️  "


class RegisterSet:
    """
    Represents a set of processor registers and flags.
    Provides methods to get, set, and display registers, as well as update
    flag values based on assembly operations.
    """

    def __init__(self) -> None:
        """
        Initializes processor registers and flags.
        Sets up a dictionary to track the previous values of registers before any changes.
        """
        self.registers = {
            'AX': 0, 'BX': 0, 'CX': 0, 'DX': 0,
            'SP': 0, 'BP': 0, 'SI': 0, 'DI': 0,
            'CS': 0, 'DS': 0, 'SS': 0, 'ES': 0, 'FS': 0, 'GS': 0
        }
        # Flags: Zero (ZF), Sign (SF), Parity (PF), and Carry (CF)
        self.flags = {'ZF': 0, 'SF': 0, 'PF': 0, 'CF': 0}

        # Diccionario para rastrear los valores anteriores de los registros
        self.last_values = self.registers.copy()
        self.registers_supported = list(self.registers.keys())
        self.terminal = Terminal()

    @dispatch(str)
    def get(self, reg: str) -> int:
        """
        Retrieves the value of the specified register.

        Args:
            reg (str): Name of the register.

        Returns:
            int: Current value of the specified register.
        """
        return self.registers.get(reg.upper(), None)

    @dispatch(str, int)
    def set(self, reg: str, value: int) -> None:
        """
        Sets a value in the specified register and updates the previous value.

        Args:
            reg (str): Name of the register.
            value (int): Value to set in the register.

        Returns:
            None
        """
        reg = reg.upper()
        if reg in self.registers:
            # Guarda el valor actual en last_values antes de actualizar
            self.last_values[reg] = self.registers[reg]
            self.registers[reg] = value & 0xFFFF

    def update_flags(self, result: int, operation: Optional[str] = None, carry: Optional[bool] = None) -> None:
        """Updates ZF, SF, PF and (optionally) CF on a 16-bit result.

        - ZF/SF: computed over 16 bits
        - PF: even parity of the low 8 bits (8086 semantics)
        - CF: updated only when the operation defines it and `carry` is provided
        """
        r16 = result & 0xFFFF
        self.flags['ZF'] = 1 if r16 == 0 else 0
        self.flags['SF'] = 1 if (r16 & 0x8000) != 0 else 0
        self.flags['PF'] = 1 if (bin(r16 & 0xFF).count('1') % 2 == 0) else 0

        op = (operation or '').upper()
        if op in ('ADD', 'SUB', 'SHL', 'SHR', 'ROL', 'ROR') and carry is not None:
            self.flags['CF'] = 1 if carry else 0

# en la clase donde está print_changed_registers (p.ej. CpuX8086)

    def print_changed_registers(
        self,
        out: Optional[Callable[[str], None]] = None,
        use_colors: bool = True,
    ) -> None:
        """
        Emite solo los registros cuyo valor cambió desde la última ejecución.
        - out: función para emitir líneas (por defecto: print)
        - use_colors: si False, quita códigos ANSI (útil para web que no los renderiza)
        """
        if out is None:
            out = print

        # Aseguramos snapshot previo para comparar
        last = getattr(self, "last_values", None)
        if last is None:
            last = {}
        # Si no hay snapshot previo, usamos el estado actual para evitar KeyError
        if not last:
            self.last_values = dict(self.registers)

        c = AnsiColors

        def emit(line: str):
            if not use_colors:
                # strip ANSI
                line = re.sub(r"\x1b\[[0-9;]*m", "", line)
            out(line)

        emit(f"{c.BRIGHT_YELLOW.value}{'Register':<8} {'Decimal':<10} {'Hexadecimal':<12} {'Binary':<18}{c.RESET.value}")
        emit(c.BRIGHT_BLACK.value + "-" * 50 + c.RESET.value)

        for reg, value in self.registers.items():
            prev = self.last_values.get(reg, None)
            if prev is None or value != prev:
                dec_value = value
                hex_value = f"0x{value:04X}"
                bin_value = f"{value:016b}"
                emit(
                    f"{c.BRIGHT_GREEN.value}{reg:<8} "
                    f"{c.BRIGHT_WHITE.value}{dec_value:<10} "
                    f"{c.BRIGHT_BLUE.value}{hex_value:<12} "
                    f"{c.BRIGHT_CYAN.value}{bin_value:<18}{c.RESET.value}"
                )

        emit(c.BRIGHT_BLACK.value + "-" * 50 + c.RESET.value)

        # Actualizamos snapshot para la próxima comparación
        self.last_values = dict(self.registers)


    def print_registers(self) -> None:
        """
        Prints all registers and flags in decimal, hexadecimal, and binary formats.

        Returns:
            None
        """
        self.terminal.info_message(
            f"{'Register':<8} {'Decimal':<10} {'Hexadecimal':<12} {'Binary':<18}")
        self.terminal.info_message("-" * 50)
        for reg, value in self.registers.items():
            dec_value = value
            hex_value = f"0x{value:04X}"
            bin_value = f"{value:016b}"
            self.terminal.info_message(
                f"{reg:<8} {dec_value:<10} {hex_value:<12} {bin_value:<18}")

        # Print the flags below the registers
        self.terminal.info_message("\nStatus Flags:")
        self.terminal.info_message(f"Zero Flag (ZF): {self.flags['ZF']}")
        self.terminal.info_message(f"Sign Flag (SF): {self.flags['SF']}")
        self.terminal.info_message(f"Parity Flag (PF): {self.flags['PF']}")
        self.terminal.info_message(f"Carry Flag (CF): {self.flags['CF']}")

    def set_register_upper(self, reg: int, value: int) -> int:
        """Set the upper 8 bits of a 16-bit register to a new value.

        Args:
            reg (int): 16bit value
            value (int): 8bit value

        Returns:
            int: 16bit value with the upper 8 bits set to the new value.
        """
        reg = (reg & 0x00ff) | (value << 8)
        return reg

    def set_register_lower(self, reg: int, value: int) -> int:
        """Set the lower 8 bits of a 16-bit register to a new value.

        Args:
            reg (int): 16bit value
            value (int): 8bit value

        Returns:
            int: 16bit value with the lower 8 bits set to the new value.
        """

        # Clear the lower 8 bits of the register
        reg &= 0xFF00

        # Set the lower 8 bits of the register to the new value
        reg |= value

        return reg


class InstructionParser:
    """
    Parses and executes assembly instructions, handling arithmetic and bitwise operations
    on registers, and providing detailed error messages.
    """

    def __init__(self) -> None:
        """
        Configures the lexer and parser to analyze assembly instructions.
        Initializes the maps of instruction methods and machine codes.
        """
        # Configuración de lexer y parser
        self.lexer = LexerGenerator()
        self.lexer.add(
            "OPCODE", r"(?i)mov|add|sub|and|or|xor|not|neg|inc|dec|shl|shr|rol|ror|push|pop|int")
        self.lexer.add(
            "REGISTER", r"(?i)AX|BX|CX|DX|SP|BP|SI|DI|CS|DS|SS|ES|FS|GS")
        self.lexer.add("NUMBER", r"0b[01]+|0x[0-9a-fA-F]+|\d+")
        self.lexer.add("COMMA", r",")
        self.lexer.add("COMMENT", r";.*")
        self.lexer.ignore(r"\s+")
        self.lexer = self.lexer.build()

        self.pg = ParserGenerator(["OPCODE", "REGISTER", "NUMBER", "COMMA"])
        self.pg.production("instruction : OPCODE operands")(
            self.handle_instruction)
        self.pg.production("operands : operand COMMA operand")(
            self.operands_multiple)
        self.pg.production("operand : REGISTER")(self.operand_register)
        self.pg.production("operand : NUMBER")(self.operand_number)
        self.pg.error(self.handle_parse_error)
        self.parser = self.pg.build()
        self.terminal = Terminal()

        self.opcode_map = {
            'MOV': {'reg, imm16': 'B8', 'reg, reg': '8B', 'mem, reg': '8B', 'reg, mem': '8A'},
            'ADD': {'reg, imm16': '05', 'reg, reg': '01'},
            'SUB': {'reg, imm16': '2D', 'reg, reg': '29'},
            'AND': {'reg, imm16': '25', 'reg, reg': '21'},
            'OR': {'reg, imm16': '0D', 'reg, reg': '09'},
            'XOR': {'reg, imm16': '35', 'reg, reg': '31'},
            'INC': {'reg': '40'},
            'DEC': {'reg': '48'},
            'SHL': {'reg': 'D0E0'},
            'SHR': {'reg': 'D0E8'},
            'ROL': {'reg': 'D0C0'},
            'ROR': {'reg': 'D0C8'},
            'NOT': {'reg': 'F7D0'},
            'NEG': {'reg': 'F7D8'},
            'PUSH': {'reg': '50'},
            'POP': {'reg': '58'},
            'INT': ['0x21'],
        }

        self.mnemonic_map = {
            'B8': 'MOV reg, imm16', '89': 'MOV reg, reg', '8B': 'MOV mem, reg', '8A': 'MOV reg, mem',
            '05': 'ADD reg, imm16', '01': 'ADD reg, reg',
            '2D': 'SUB reg, imm16', '29': 'SUB reg, reg',
            '25': 'AND reg, imm16', '21': 'AND reg, reg',
            '0D': 'OR reg, imm16',  '09': 'OR reg, reg',
            '35': 'XOR reg, imm16', '31': 'XOR reg, reg',
            '40': 'INC reg', '48': 'DEC reg',
            'D0E0': 'SHL reg', 'D0E8': 'SHR reg',
            'D0C0': 'ROL reg', 'D0C8': 'ROR reg',
            'F7D0': 'NOT reg', 'F7D8': 'NEG reg',
            '50': 'PUSH reg', '58': 'POP reg',
        }

        self.opcode_methods = {
            'MOV': self.asm_mov,
            'ADD': self.asm_add,
            'SUB': self.asm_sub,
            'AND': self.asm_and,
            'OR': self.asm_or,
            'XOR': self.asm_xor,
            'NOT': self.asm_not,
            'NEG': self.asm_neg,
            'INC': self.asm_inc,
            'DEC': self.asm_dec,
            'SHL': self.asm_shl,
            'SHR': self.asm_shr,
            'ROL': self.asm_rol,
            'ROR': self.asm_ror,
            'PUSH': self.asm_push,
            'POP': self.asm_pop,
        }

        # Lista de instrucciones soportadas
        self.supported_instructions = list(self.opcode_methods.keys())

        # Mapeo de registros a sus correspondientes códigos binarios
        self.register_codes = {
            'AX': '000', 'CX': '001', 'DX': '010', 'BX': '011',
            'SP': '100', 'BP': '101', 'SI': '110', 'DI': '111'
        }

        # --- dispatch table ---
        self.functions_map = {
            'MOV':  self.asm_mov,
            'ADD':  self.asm_add,
            'SUB':  self.asm_sub,
            'AND':  self.asm_and,
            'OR':   self.asm_or,
            'XOR':  self.asm_xor,
            'INC':  self.asm_inc,
            'DEC':  self.asm_dec,
            'SHL':  self.asm_shl,
            'SHR':  self.asm_shr,
            'ROL':  self.asm_rol,
            'ROR':  self.asm_ror,
            # opcionales (si los agregaste)
            'NEG':  getattr(self, 'asm_neg',  None) or (lambda *_: ().throw(NotImplementedError("NEG no implementado"))),
            'NOT':  getattr(self, 'asm_not',  None) or (lambda *_: ().throw(NotImplementedError("NOT no implementado"))),
            'PUSH': self.asm_push,
            'POP':  self.asm_pop,
            'INT':  self.asm_int,   # recuerda: parse() le pasa (operands, memory)
        }
        # Filtrar los Nones por si NEG/NOT no están
        self.functions_map = {k: v for k, v in self.functions_map.items() if v}

        self.supported_instructions = sorted(self.functions_map.keys())

        # Instancia de RegisterSet
        self.register_collection = RegisterSet()
        self.supported_registers = self.register_collection.registers_supported

        # --- tracing / stepping ---
        self.trace_enabled: bool = False
        # por defecto usa Terminal.default_message o print
        self._trace_out: Optional[Callable[[str], None]] = None

        # Programa para step/breakpoints (opcional)
        self.step_mode: bool = False
        self.program: List[str] = []     # líneas ASM
        self.labels: Dict[str, int] = {}  # label -> índice (pc)
        self.pc: int = 0
        self.base_addr: int = 0x0000
        self.breakpoints: set[int] = set()

        # Watches
        self.watches: List[str] = []
        self._watch_last: Dict[str, Optional[int]] = {}
        self.trace_color: bool = True

    def load_program(self, lines: List[str], base_addr: int = 0x0000) -> None:
        """
        Carga un listado de instrucciones (cada línea) y extrae labels 'mi_label:' al inicio de línea.
        """
        self.program = []
        self.labels.clear()
        self.pc = 0
        self.base_addr = base_addr
        for idx, line in enumerate(lines):
            raw = line.strip()
            if not raw:
                continue
            if raw.endswith(":") and " " not in raw:
                label = raw[:-1].strip()
                self.labels[label.upper()] = len(self.program)
            else:
                self.program.append(raw)
        self.step_mode = True

    def add_breakpoint(self, target: str | int) -> None:
        addr = self._resolve_bp(target)
        self.breakpoints.add(addr)

    def remove_breakpoint(self, target: str | int) -> None:
        addr = self._resolve_bp(target)
        self.breakpoints.discard(addr)

    def clear_breakpoints(self) -> None:
        self.breakpoints.clear()

    def _resolve_bp(self, target: str | int) -> int:
        if isinstance(target, int):
            return target
        t = target.strip()
        if t.upper() in self.labels:
            return self.base_addr + self.labels[t.upper()]
        # número (0x.. o decimal)
        return int(t, 16) if t.upper().startswith("0X") else int(t)

    def step(self, memory) -> Optional[str]:
        """
        Ejecuta 1 instrucción del programa cargado (step_mode) respetando breakpoints.
        Devuelve la línea ejecutada o None si terminó.
        """
        if not self.step_mode or self.pc >= len(self.program):
            return None
        cur_addr = self.base_addr + self.pc
        if cur_addr in self.breakpoints:
            self._out(f"[break] en {cur_addr:04X}")
            return self.program[self.pc]
        line = self.program[self.pc]
        self.parse(line, memory)  # esto avanzará pc +1 al final
        return line

    def cont(self, memory, max_steps: int = 10_000) -> None:
        steps = 0
        while self.step_mode and self.pc < len(self.program):
            cur_addr = self.base_addr + self.pc
            if cur_addr in self.breakpoints and steps > 0:
                self._out(f"[break] en {cur_addr:04X}")
                return
            self.step(memory)
            steps += 1
            if steps >= max_steps:
                self._out("[cont] límite de pasos alcanzado")
                return

    def disassemble_line(self, line: str, addr: Optional[int] = None) -> str:
        line = line.strip()
        if not line or line.endswith(":"):
            return line
        parts = line.split(None, 1)
        op = parts[0].upper()
        ops = [p.strip() for p in parts[1].split(',')
               ] if len(parts) > 1 else []
        b = self._encode_pseudo_bytes(op, ops)
        bhex = "-" if not b else " ".join(f"{x:02X}" for x in b)
        prefix = f"{addr:04X}: " if addr is not None else ""
        return f"{prefix}{op} " + (", ".join(ops) if ops else "") + f"    ; bytes(pseudo): {bhex}"

    def disassemble_program(self, base_addr: Optional[int] = None) -> List[str]:
        if not self.program:
            return []
        ba = self.base_addr if base_addr is None else base_addr
        out = []
        pc = 0
        for i, line in enumerate(self.program):
            out.append(self.disassemble_line(line, ba + pc))
            pc += 1  # 1 línea = 1 "longitud" educativa (no real)
        return out

    # --- helpers para ensamblado ---
    def _imm_from(self, tok: str) -> int:
        s = tok.strip()
        if s.lower().endswith('h'):
            return int(s[:-1], 16)
        if s.lower().startswith('0x'):
            return int(s, 16)
        if s.lower().startswith('0b'):
            return int(s, 2)
        return int(s)

    def assemble_line(self, line: str) -> List[int]:
        """
        Ensambla UNA línea ASM → lista de bytes (educativo, subset).
        No ejecuta la instrucción ni toca registros.
        """
        # quitar comentarios
        line = line.split(';', 1)[0].strip()
        if not line:
            return []

        # labels como "L1:" no generan bytes
        if re.match(r"^[A-Za-z_]\w*:$", line):
            return []

        parts = re.split(r"\s+", line, maxsplit=1)
        opcode = parts[0].upper()
        ops = [o.strip() for o in parts[1].split(',')
               ] if len(parts) > 1 else []

        # helpers
        regcodes = self.register_codes  # e.g. 'AX' -> '000'

        def reg_index(r: str) -> int:
            r = r.upper()
            if r not in regcodes:
                raise ValueError(f"Registro no soportado: {r}")
            return int(regcodes[r], 2)

        def imm_from(s: str) -> int:
            return self._imm_from(s)

        # INT inmediato (p.ej. INT 0x21)
        if opcode == 'INT':
            if len(ops) != 1:
                raise ValueError("INT: se esperaba un operando (vector)")
            vec = imm_from(ops[0])
            return [0xCD, vec & 0xFF]

        # MOV reg,reg (0x8B + modrm) y MOV reg,imm16 (B8+reg lo/hi)
        if opcode == 'MOV' and len(ops) == 2:
            dst, src = ops[0].upper(), ops[1].upper()
            if src in self.register_collection.registers and dst in self.register_collection.registers:
                op_hex = '8B'
                modrm = (0xC0 | (reg_index(dst) << 3) | reg_index(src)) & 0xFF
                return [int(op_hex, 16), modrm]
            if dst in self.register_collection.registers:
                imm = imm_from(src)
                base = int('B8', 16)
                opbyte = (base + reg_index(dst)) & 0xFF
                return [opbyte, imm & 0xFF, (imm >> 8) & 0xFF]

        # PSEUDO-ENCODING educativo para ADD/SUB/AND/OR/XOR
        if opcode in ('ADD', 'SUB', 'AND', 'OR', 'XOR') and len(ops) == 2:
            dst, src = ops[0].upper(), ops[1]
            if dst not in self.register_collection.registers:
                raise ValueError(f"{opcode}: destino no es registro: {dst}")

            # bases por instrucción
            bases = {
                'ADD': {'imm': 0x70, 'rr': 0x10},
                'SUB': {'imm': 0x71, 'rr': 0x11},
                'AND': {'imm': 0x72, 'rr': 0x12},
                'OR': {'imm': 0x73, 'rr': 0x13},
                'XOR': {'imm': 0x74, 'rr': 0x14},
            }
            base_imm = bases[opcode]['imm']
            base_rr = bases[opcode]['rr']

            # reg, reg → [base_rr, modrm]
            if isinstance(src, str) and src.upper() in self.register_collection.registers:
                modrm = (0xC0 | (reg_index(dst) << 3) |
                         reg_index(src.upper())) & 0xFF
                return [base_rr & 0xFF, modrm]

            # reg, imm16 → [base_imm, REG[dst], lo, hi]
            imm = imm_from(src)
            return [base_imm & 0xFF, reg_index(dst) & 0xFF, imm & 0xFF, (imm >> 8) & 0xFF]

        # INC/DEC reg (0x40/0x48 + reg)
        if opcode in ('INC', 'DEC') and len(ops) == 1:
            base = int(self.opcode_map[opcode]['reg'], 16)  # "40" o "48"
            return [(base + reg_index(ops[0])) & 0xFF]

        # PUSH/POP reg (0x50/0x58 + reg)
        if opcode in ('PUSH', 'POP') and len(ops) == 1:
            base = int(self.opcode_map[opcode]['reg'], 16)  # "50" o "58"
            return [(base + reg_index(ops[0])) & 0xFF]

        # (Opcional) otros monádicos (SHL/SHR/ROL/ROR/NOT/NEG) → sin ensamblado real aún
        raise ValueError(f"assemble_line: instrucción no soportada: '{line}'")

    def monitor(self, cmd: str, memory) -> None:
        """
        Comandos:
        - trace on|off
        - bp <label|addr>
        - delbp <label|addr>
        - watch <expr>
        - unwatch <expr>
        - step
        - cont
        - disas
        """
        t = cmd.strip().split(None, 1)
        if not t:
            return
        c = t[0].lower()
        arg = t[1] if len(t) > 1 else ""

        if c == "trace":
            on = arg.strip().lower() == "on"
            self.enable_trace(on)
            self._out(f"[trace] {'on' if on else 'off'}")
        elif c == "bp":
            self.add_breakpoint(arg)
            self._out(f"[bp] agregado {arg}")
        elif c == "delbp":
            self.remove_breakpoint(arg)
            self._out(f"[bp] eliminado {arg}")
        elif c == "watch":
            self.add_watch(arg)
            self._out(f"[watch] {arg}")
        elif c == "unwatch":
            self.remove_watch(arg)
            self._out(f"[unwatch] {arg}")
        elif c == "step":
            line = self.step(memory)
            if line is None:
                self._out("[step] fin de programa")
        elif c == "cont":
            self.cont(memory)
        elif c == "disas":
            for l in self.disassemble_program():
                self._out(l)
        else:
            self._out(f"[?] comando desconocido: {c}")

    def handle_instruction(self, p: list) -> None:
        """
        Calls the appropriate operation method based on the opcode.

        Args:
            p (list): List of instruction tokens.

        Returns:
            None
        """
        opcode = p[0].getstr().upper()
        operands = p[1]
        method = self.opcode_methods.get(opcode)
        if method:
            try:
                method(operands)
            except Exception as e:
                self.terminal.error_message(
                    f"Execution error in '{opcode} {operands}': {e}")
        else:
            self.terminal.error_message(f"Unsupported instruction '{opcode}'.")

    def operands_multiple(self, p: list) -> list:
        """
        Converts a list of operands into a manageable list of two elements.

        Args:
            p (list): List of operand tokens.

        Returns:
            list: List containing the first and third tokens.
        """
        return [p[0], p[2]]

    def operand_register(self, p: list) -> str:
        """
        Gets the register name in uppercase.

        Args:
            p (list): Register token.

        Returns:
            str: Register name in uppercase.
        """
        return p[0].getstr().upper()

    def operand_number(self, p: list) -> Optional[int]:
        """
        Converts a number from binary, hexadecimal, or decimal to decimal format.

        Args:
            p (list): Number token in binary, hexadecimal, or decimal format.

        Returns:
            int: Decimal value of the number.
        """
        value = p[0].getstr()
        # Detecta el formato y convierte el valor
        try:
            if value.startswith("0b"):
                return int(value, 2)  # Binario
            elif value.startswith("0x"):
                return int(value, 16)  # Hexadecimal
            else:
                return int(value)  # Decimal
        except ValueError:
            self.terminal.error_message(
                f"Invalid number format '{value}'. Expected binary (0b), hex (0x), or decimal.")
            return None

    def handle_parse_error(self, token) -> None:
        """
        Displays an error message when a syntax error occurs in the parser.

        Args:
            token (Token): Token that caused the syntax error.

        Returns:
            None
        """
        self.terminal.error_message(
            f"Unexpected token '{token.getstr()}' at position {token.getsourcepos().idx}.")
        self.terminal.info_message(
            "TIP: Check the instruction format. An instruction should follow 'OPCODE REGISTER, NUMBER' or 'OPCODE REGISTER, REGISTER'.")

    def parse(self, instruction: str, memory: Memory, dry_run: bool = False) -> Optional[dict]:
        """
        Parses a single assembly instruction, executes it, and returns its details.

        Args:
            instruction (str): Assembly instruction as a text string.
            memory (Memory): Memory object representing the system's memory.

        Returns:
            dict: Parsed tokens including opcode and operands.

        Raises:
            ValueError: If the instruction format is invalid.
            KeyError: If the opcode is not supported.
        """
        """
        Parses a single assembly instruction, executes it, and (opcionalmente) retorna tokens.
        """

        """
        Parsea una instrucción. Si dry_run=True, NO ejecuta; devuelve tokens {'opcode','operands'}.
        Caso contrario, ejecuta como antes (traza, watches, etc.).
        """
        # referencia a memoria (para PUSH/POP/INT cuando se ejecute)
        self._mem = memory

        cmd = instruction.strip()
        if not cmd:
            return None

        # Normalización básica
        parts = cmd.split(None, 1)
        opcode = parts[0].upper()
        operands = [p.strip() for p in parts[1].split(',')
                    ] if len(parts) > 1 else []

        # --- Modo "solo parseo" (para assemble) ---
        if dry_run:
            return {'opcode': opcode, 'operands': operands}

        # --- A partir de acá es el camino de ejecución "normal" ---
        # Breakpoints solo si estamos en modo programa (step_mode)
        if self.step_mode:
            cur_addr = self.base_addr + self.pc
            if cur_addr in self.breakpoints:
                self._out(f"[break] en {cur_addr:04X}")
                return  # nos detenemos sin ejecutar

        # Envolver memoria si hay traza (para registrar accesos)
        traced_mem = TracedMemory(memory) if self.trace_enabled else memory

        if opcode not in self.functions_map:
            raise ValueError(f"Unsupported instruction: {opcode}")

        before_regs, before_flags = self._snapshot()

        # Ejecutar (INT recibe memoria)
        fn = self.functions_map[opcode]
        if opcode == 'INT':
            fn(operands, traced_mem)
        else:
            fn(operands)

        after_regs, after_flags = self._snapshot()

        # Traza
        if self.trace_enabled:
            rec = TraceRecord(
                opcode=opcode,
                operands=operands,
                pseudo_bytes=self._encode_pseudo_bytes(opcode, operands),
                regs_before=before_regs, regs_after=after_regs,
                flags_before=before_flags, flags_after=after_flags,
                mem_accesses=(traced_mem.accesses if isinstance(
                    traced_mem, TracedMemory) else [])
            )
            self._out(self._format_trace(rec))

        # Watches
        self._eval_watches(traced_mem)

        # Avanzar PC en modo step
        if self.step_mode:
            self.pc = min(self.pc + 1, max(0, len(self.program) - 1))

        return None

    def add_watch(self, expr: str) -> None:
        if expr not in self.watches:
            self.watches.append(expr)
            self._watch_last[expr] = None

    def remove_watch(self, expr: str) -> None:
        if expr in self.watches:
            self.watches.remove(expr)
            self._watch_last.pop(expr, None)

    def asm_int(self, operands: List[str], memory) -> None:
        """
        INT <vector>
        Soporta INT 0x21 con servicios: AH=09h, 0Ah, 4Ch.
        - 09h: imprime cadena en DS:DX hasta '$'
        - 0Ah: lee buffer en DS:DX (long máx en [DS:DX], long real en [DS:DX+1], datos a partir de [DS:DX+2], termina con 0x00)
        - 4Ch: termina con código en AL
        """
        if not operands:
            raise ValueError("INT: falta vector")

        tok = operands[0].strip().upper()
        try:
            vec = int(tok, 16) if tok.startswith('0X') else int(tok)
        except ValueError:
            raise ValueError(f"INT: vector inválido '{operands[0]}'")

        if vec != 0x21:
            raise ValueError(f"INT 0x{vec:02X} no soportada (sólo 0x21)")

        ax = self.register_collection.get('AX')
        ah = (ax >> 8) & 0xFF
        # alias dict (por compatibilidad)
        registers = self.register_collection.registers

        if ah == 0x09:
            self.service_09(memory, registers)
        elif ah == 0x0A:
            self.service_0a(memory, registers)
        elif ah == 0x4C:
            self.service_4c(registers)
        else:
            raise ValueError(f"INT 0x21: función AH=0x{ah:02X} no soportada")

    def clear_watches(self) -> None:
        self.watches.clear()
        self._watch_last.clear()

    def _eval_watches(self, memory) -> None:
        for expr in list(self.watches):
            try:
                val = self._eval_expr(expr, memory)
            except Exception as e:
                self._out(f"[watch err] {expr}: {e}")
                continue
            last = self._watch_last.get(expr)
            if last is None:
                self._watch_last[expr] = val
            elif last != val:
                self._out(f"[watch] {expr}: {last:04X}->{val:04X}")
                self._watch_last[expr] = val

    def _eval_expr(self, expr: str, memory) -> int:
        e = expr.strip().upper()
        if e.startswith("FLAGS."):
            f = e.split(".", 1)[1]
            return int(self.register_collection.flags.get(f, 0))
        if e in self.register_collection.registers:
            return int(self.register_collection.get(e))
        if e.startswith("[") and e.endswith("]"):
            inside = e[1:-1]
            # [DS:DX]
            if ":" in inside:
                left, right = inside.split(":", 1)
                if left == "DS" and right == "DX":
                    ds = self.register_collection.get('DS')
                    dx = self.register_collection.get('DX')
                    addr = (ds << 4) + dx
                    page = getattr(memory, 'active_page', 0)
                    return int(memory.peek(page, addr))
                else:
                    # [page:addr]
                    page_s, addr_s = left, right
                    page = int(page_s, 16) if page_s.startswith(
                        "0X") else int(page_s)
                    addr = int(addr_s, 16) if addr_s.startswith(
                        "0X") else int(addr_s)
                    return int(memory.peek(page, addr))
            # [addr] (usa active_page)
            addr_s = inside
            addr = int(addr_s, 16) if addr_s.startswith("0X") else int(addr_s)
            page = getattr(memory, 'active_page', 0)
            return int(memory.peek(page, addr))
        # número inmediato
        return int(e, 16) if e.startswith("0X") else int(e)

    def int_0x21(self, ah: int, memory: dict, registers: dict) -> None:
        """
        Simula la interrupción 0x21 para servicios básicos de DOS.

        Args:
            ah (int): El registro AH contiene el número del servicio.
            memory (dict): Simulación de la memoria del sistema.
            registers (dict): Registros del procesador (AX, BX, CX, etc.).

        Returns:
            None
        """

        print('''
            Welcome to INT21:
            ~~~~~~~~~~~~~~~~~
            Only a few services are supported:

            - Service 0x09: Print strings terminated in '$'.
            - Service 0x0A: Read strings with a limit.
            - Service 0x4C: End program. ''')

        if ah == 0x09:  # Mostrar cadena terminada en '$'
            self.service_09(memory, registers)
        elif ah == 0x0A:  # Leer cadena con límite
            self.service_0a(memory, registers)
        elif ah == 0x4C:  # Terminar programa
            self.service_4c(registers)
        else:
            raise ValueError(f"Unsupported INT 0x21 service: 0x{ah:02X}")

    def enable_trace(self, enabled: bool = True, out: Optional[Callable[[str], None]] = None, color: Optional[bool] = None) -> None:
        """
        Activa/desactiva la traza. Si 'out' es None, se imprime con Terminal.
        En ese caso, si 'colored' es True (o self.trace_color ya es True),
        se agregan colores ANSI. Si se pasa 'out', no se colorea para no
        contaminar salidas de tests/logging.
        """
        self.trace_enabled = enabled
        self.trace_enabled = enabled
        self._trace_out = out
        if color is not None:
            self.trace_color = color

    def _out(self, msg: str) -> None:

        # Si hay callback externo (tests/logging), respetamos el callback (sin color).
        if self._trace_out:
            self._trace_out(msg)
            return

         # Interactivo: si el mensaje contiene ANSI y trace_color está activo,
         # imprimir "raw" para no perder los colores.
        if self.trace_color and "\x1b[" in msg:
            print(msg)
            return

        # Caso general: usar el terminal.
        try:
            self.terminal.default_message(msg)
        except Exception:
            print(msg)

    def _snapshot(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        return (dict(self.register_collection.registers),
                dict(self.register_collection.flags))

    def _diff_dict(self, before: Dict[str, int], after: Dict[str, int], only_changes=True) -> List[str]:
        items = []
        for k in sorted(after.keys()):
            b, a = before.get(k), after.get(k)
            if only_changes and b == a:
                continue
            if k in ('AX', 'BX', 'CX', 'DX', 'SP', 'BP', 'SI', 'DI', 'DS', 'ES'):
                items.append(f"{k}:{b:04X}->{a:04X}")
            else:
                items.append(f"{k}:{b}->{a}")
        return items

    def _fmt_mem(self, mem_accesses: List[Tuple[str, int, int, int]], max_items: int = 4) -> str:
        if not mem_accesses:
            return "-"
        parts = []
        for i, (rw, page, addr, val) in enumerate(mem_accesses):
            if i >= max_items:
                parts.append(f"...(+{len(mem_accesses)-max_items})")
                break
            parts.append(f"{rw}[p{page}:{addr:04X}]={val:02X}")
        return " ".join(parts)

    def _encode_pseudo_bytes(self, opcode: str, operands: List[str]) -> Optional[List[int]]:
        """
        Mini codificador educativo (NO 8086 real). Solo para mostrar 'bytes (pseudo)' en la traza.
        Reg mapa: AX=0,BX=3,CX=1,DX=2,SP=4,BP=5,SI=6,DI=7
        """
        reg_ix = {'AX': 0, 'CX': 1, 'DX': 2, 'BX': 3,
                  'SP': 4, 'BP': 5, 'SI': 6, 'DI': 7}
        op = opcode.upper()
        try:
            if op == 'MOV' and len(operands) == 2:
                d, s = operands[0].upper(), operands[1].upper()
                if d in reg_ix:
                    if s.startswith('0X') or s.isdigit():
                        imm = int(s, 16) if s.startswith('0X') else int(s)
                        # MOV reg, imm (pseudo)
                        return [0xB8 + reg_ix[d], imm & 0xFF, (imm >> 8) & 0xFF]
                    elif s in reg_ix:
                        # MOV reg, reg (pseudo)
                        return [0x8B, 0xC0 | (reg_ix[d] << 3) | reg_ix[s]]
            if op in ('ADD', 'SUB') and len(operands) == 2:
                d, s = operands[0].upper(), operands[1].upper()
                if d in reg_ix:
                    if s.startswith('0X') or s.isdigit():
                        imm = int(s, 16) if s.startswith('0X') else int(s)
                        base = 0x70 if op == 'ADD' else 0x71
                        # pseudo
                        return [base, reg_ix[d], imm & 0xFF, (imm >> 8) & 0xFF]
                    elif s in reg_ix:
                        base = 0x10 if op == 'ADD' else 0x11
                        return [base, 0xC0 | (reg_ix[d] << 3) | reg_ix[s]]
            if op in ('AND', 'OR', 'XOR', 'INC', 'DEC', 'SHL', 'SHR', 'ROL', 'ROR', 'NEG', 'NOT', 'PUSH', 'POP'):
                return [hash(op) & 0xFF]  # marcador simbólico
            if op == 'INT':
                v = operands[0]
                imm = int(v, 16) if v.upper().startswith('0X') else int(v)
                return [0xCD, imm & 0xFF]
        except Exception:
            return None
        return None

    def _format_trace(self, rec: TraceRecord) -> str:
        mnem = f"{rec.opcode} " + \
            (", ".join(rec.operands) if rec.operands else "")
        b = "-" if not rec.pseudo_bytes else " ".join(
            f"{x:02X}" for x in rec.pseudo_bytes)
        regs = self._diff_dict(rec.regs_before, rec.regs_after)
        flags = self._diff_dict(rec.flags_before, rec.flags_after)
        mems = self._fmt_mem(rec.mem_accesses)

        # ¿Coloreamos? Solo si no hay callback externo (CLI interactivo)
        use_color = (self._trace_out is None) and self.trace_color
        if not use_color:
            regs_s = "[" + ", ".join(regs) + "]" if regs else "[]"
            flags_s = "[" + ", ".join(flags) + "]" if flags else "[]"
            return f"{mnem}  | bytes(pseudo): {b}  | regsΔ: {regs_s}  | flagsΔ: {flags_s}  | mem: {mems}"

        C = AnsiColors
        mnem_c = f"{C.BRIGHT_YELLOW.value}{mnem}{C.RESET.value}"
        bytes_c = f"{C.BRIGHT_BLACK.value}bytes(pseudo):{C.RESET.value} {C.BRIGHT_BLUE.value}{b}{C.RESET.value}"
        regs_s = "[" + ", ".join(regs) + "]" if regs else "[]"
        flags_s = "[" + ", ".join(flags) + "]" if flags else "[]"
        regs_c = f"{C.BRIGHT_BLACK.value}regsΔ:{C.RESET.value} {C.BRIGHT_GREEN.value}{regs_s}{C.RESET.value}"
        flags_c = f"{C.BRIGHT_BLACK.value}flagsΔ:{C.RESET.value} {C.BRIGHT_MAGENTA.value}{flags_s}{C.RESET.value}"
        mem_c = f"{C.BRIGHT_BLACK.value}mem:{C.RESET.value} {C.BRIGHT_CYAN.value}{mems}{C.RESET.value}"
        return f"{mnem_c}  | {bytes_c}  | {regs_c}  | {flags_c}  | {mem_c}"

    def service_09(self, memory: Memory, registers: dict) -> None:
        # Print string at DS:DX until '$' (like DOS)
        ds = registers.get('DS')
        dx = registers.get('DX')
        address = (ds << 4) + dx

        page = memory.active_page
        output = ""
        while memory.peek(page, address) != ord('$'):
            output += chr(memory.peek(page, address))
            address += 1

        try:
            self.terminal.default_message(output, end="")
        except Exception:
            print(output, end="")

    def service_0a(self, memory: Memory, registers: dict) -> None:
        # Buffered input at DS:DX
        ds = registers.get('DS')
        dx = registers.get('DX')
        address = (ds << 4) + dx

        page = memory.active_page
        max_length = memory.peek(page, address)
        address += 1

        input_str = input("Enter string: ")[:max_length]
        memory.poke(page, address, len(input_str))  # Actual length
        address += 1

        for i, char in enumerate(input_str):
            memory.poke(page, address + i, ord(char))

        memory.poke(page, address + len(input_str), 0x00)  # End with 0x00

    def service_4c(self, registers: dict) -> None:
        # Exit with code in AL (AX low byte)
        ax = registers.get('AX')
        exit_code = ax & 0x00FF
        import sys
        raise SystemExit(exit_code)

    @dispatch(list)
    def asm_push(self, operands: List[str]) -> int:
        """
        PUSH <reg>
        Empuja 16 bits a la pila en little-endian usando Memory y actualiza SP.
        """
        if not hasattr(self, "_mem") or self._mem is None:
            raise RuntimeError(
                "asm_push: Memory no inicializada (llamar via parse/parse_instruction)")

        (src,) = operands
        reg = src.strip().upper()
        value = self.register_collection.get(reg)  # 16 bits

        # SP = SP - 2, escribir low en [SP], high en [SP+1]
        sp = (self.register_collection.get('SP') - 2) & 0xFFFF
        page = getattr(self._mem, 'active_page', 0)

        low = value & 0xFF
        high = (value >> 8) & 0xFF
        self._mem.poke(page, sp, low)
        self._mem.poke(page, sp + 1, high)

        self.register_collection.set('SP', sp)
        return value & 0xFFFF

    @dispatch(list)
    def asm_pop(self, operands: List[str]) -> int:
        """
        POP <reg>
        Saca 16 bits de la pila en little-endian usando Memory y actualiza SP.
        """
        if not hasattr(self, "_mem") or self._mem is None:
            raise RuntimeError(
                "asm_pop: Memory no inicializada (llamar via parse/parse_instruction)")

        (dst,) = operands
        reg = dst.strip().upper()

        sp = self.register_collection.get('SP')
        page = getattr(self._mem, 'active_page', 0)

        low = self._mem.peek(page, sp)
        high = self._mem.peek(page, sp + 1)
        value = ((high << 8) | low) & 0xFFFF

        self.register_collection.set(reg, value)
        self.register_collection.set('SP', (sp + 2) & 0xFFFF)
        return value

    # Operaciones de ensamblador

    @dispatch(list)
    def asm_mov(self, operands: List[str]) -> int:
        """
        MOV <reg>, <reg|imm>
        Inmediatos: acepta 0x.... o decimal; no upper-casea el string antes de parsear.
        """
        dst, src = operands
        dst = dst.upper()

        # Normalizamos para evaluar
        if isinstance(src, str):
            src_str = src.strip()
            src_up = src_str.upper()
            # Fuente = registro
            if src_up in self.register_collection.registers:
                val_src = self.register_collection.get(src_up)
            # Fuente = inmediato hex (acepta 0x o 0X)
            elif src_str.lower().startswith('0x'):
                val_src = int(src_str, 16)
            # Fuente = inmediato decimal
            elif src_str.isdigit():
                val_src = int(src_str)
            else:
                raise ValueError(f"MOV: fuente inválida {src}")
        elif isinstance(src, int):
            val_src = src
        else:
            raise ValueError(f"MOV: fuente inválida {src}")

        # Destino debe ser registro
        if dst not in self.register_collection.registers:
            raise ValueError(f"MOV: destino inválido {dst}")

        self.register_collection.set(dst, val_src & 0xFFFF)
        # Flags no se tocan en MOV
        return val_src & 0xFFFF

    @dispatch(list)
    def asm_add(self, operands: List[str]) -> int:
        dst, src = operands
        dst = dst.upper()
        a = self.register_collection.get(dst)

        if isinstance(src, str):
            src_str = src.strip()
            src_up = src_str.upper()
            if src_up in self.register_collection.registers:
                b = self.register_collection.get(src_up)
            elif src_str.lower().startswith('0x'):
                b = int(src_str, 16)
            elif src_str.isdigit():
                b = int(src_str)
            else:
                raise ValueError(f"ADD: fuente inválida {src}")
        elif isinstance(src, int):
            b = src
        else:
            raise ValueError(f"ADD: fuente inválida {src}")

        tmp = a + b
        carry = tmp > 0xFFFF
        res = tmp & 0xFFFF
        self.register_collection.set(dst, res)
        self.register_collection.update_flags(
            res, operation='ADD', carry=carry)
        return res

    @dispatch(list)
    def asm_sub(self, operands: List[str]) -> int:
        dst, src = operands
        dst = dst.upper()
        a = self.register_collection.get(dst)

        if isinstance(src, str):
            src_str = src.strip()
            src_up = src_str.upper()
            if src_up in self.register_collection.registers:
                b = self.register_collection.get(src_up)
            elif src_str.lower().startswith('0x'):
                b = int(src_str, 16)
            elif src_str.isdigit():
                b = int(src_str)
            else:
                raise ValueError(f"SUB: fuente inválida {src}")
        elif isinstance(src, int):
            b = src
        else:
            raise ValueError(f"SUB: fuente inválida {src}")

        tmp = a - b
        borrow = tmp < 0
        res = tmp & 0xFFFF
        self.register_collection.set(dst, res)
        self.register_collection.update_flags(
            res, operation='SUB', carry=borrow)
        return res

    @dispatch(list)
    def asm_and(self, operands: List[str]) -> int:
        dst, src = operands
        dst = dst.upper()
        a = self.register_collection.get(dst)

        if isinstance(src, str):
            src_str = src.strip()
            src_up = src_str.upper()
            if src_up in self.register_collection.registers:
                b = self.register_collection.get(src_up)
            elif src_str.lower().startswith('0x'):
                b = int(src_str, 16)
            elif src_str.isdigit():
                b = int(src_str)
            else:
                raise ValueError(f"AND: fuente inválida {src}")
        elif isinstance(src, int):
            b = src
        else:
            raise ValueError(f"AND: fuente inválida {src}")

        res = (a & b) & 0xFFFF
        self.register_collection.set(dst, res)
        self.register_collection.flags['CF'] = 0
        self.register_collection.update_flags(res)
        return res

    @dispatch(list)
    def asm_or(self, operands: List[str]) -> int:
        dst, src = operands
        dst = dst.upper()
        a = self.register_collection.get(dst)

        if isinstance(src, str):
            src_str = src.strip()
            src_up = src_str.upper()
            if src_up in self.register_collection.registers:
                b = self.register_collection.get(src_up)
            elif src_str.lower().startswith('0x'):
                b = int(src_str, 16)
            elif src_str.isdigit():
                b = int(src_str)
            else:
                raise ValueError(f"OR: fuente inválida {src}")
        elif isinstance(src, int):
            b = src
        else:
            raise ValueError(f"OR: fuente inválida {src}")

        res = (a | b) & 0xFFFF
        self.register_collection.set(dst, res)
        self.register_collection.flags['CF'] = 0
        self.register_collection.update_flags(res)
        return res

    @dispatch(list)
    def asm_xor(self, operands: List[str]) -> int:
        dst, src = operands
        dst = dst.upper()
        a = self.register_collection.get(dst)

        if isinstance(src, str):
            src_str = src.strip()
            src_up = src_str.upper()
            if src_up in self.register_collection.registers:
                b = self.register_collection.get(src_up)
            elif src_str.lower().startswith('0x'):
                b = int(src_str, 16)
            elif src_str.isdigit():
                b = int(src_str)
            else:
                raise ValueError(f"XOR: fuente inválida {src}")
        elif isinstance(src, int):
            b = src
        else:
            raise ValueError(f"XOR: fuente inválida {src}")

        res = (a ^ b) & 0xFFFF
        self.register_collection.set(dst, res)
        self.register_collection.flags['CF'] = 0
        self.register_collection.update_flags(res)
        return res

    def _parse_src(self, src) -> int:
        if isinstance(src, int):
            return src
        if isinstance(src, str):
            s = src.strip()
            su = s.upper()
            if su in self.register_codes:
                return self.register_collection.get(su)
            if s.lower().startswith('0x'):
                return int(s, 16)
            if s.isdigit():
                return int(s)
        raise ValueError(f"Fuente inválida {src!r}")

    @dispatch(list)
    def asm_not(self, operands: list) -> None:
        """
        Executes the NOT instruction, performing a bitwise NOT on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            result = ~self.register_collection.get(dest) & 0xFFFF
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result)
        except KeyError:
            self.terminal.error_message(
                f"Invalid register '{dest}' in NOT operation.")
            self.terminal.info_message(
                "TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_neg(self, operands: list) -> None:
        """
        Executes the NEG instruction, negating the value of a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        try:
            dest = operands[0]
            if dest not in self.register_collection.registers_supported:
                raise KeyError(f"Invalid register '{dest}' for INC operation.")

            result = -self.register_collection.get(dest) & 0xFFFF
            self.register_collection.set(dest, result)
            self.register_collection.update_flags(result, operation='SUB')
        except KeyError:
            self.terminal.error_message(
                f"Invalid register '{dest}' in NEG operation.")
            self.terminal.info_message(
                "TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_inc(self, operands: list) -> int:
        """
        Executes the INC instruction, incrementing the value of a register by one.

        Args:
            operands (list): List of operands (destination).

        Returns:
            result: The incremented value of the register.
        """

        try:
            dest = operands[0]
            if dest not in self.register_collection.registers_supported:
                raise KeyError(f"Invalid register '{dest}' for INC operation.")
            result = self.register_collection.get(dest) + 1
            self.register_collection.set(dest, result & 0xFFFF)
            self.register_collection.update_flags(result)
            return result
        except KeyError:
            self.terminal.error_message(
                f"Invalid register '{dest}' in INC operation.")
            self.terminal.info_message(
                "TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_dec(self, operands: list) -> int:
        """
        Executes the DEC instruction, decrementing the value of a register by one.

        Args:
            operands (list): List of operands (destination).

        Returns:
            result : The decremented value of the register.
        """
        try:
            dest = operands[0]
            if dest not in self.register_collection.registers_supported:
                raise KeyError(f"Invalid register '{dest}' for INC operation.")
            result = self.register_collection.get(dest) - 1
            self.register_collection.set(dest, result & 0xFFFF)
            self.register_collection.update_flags(result, operation='SUB')
            return result
        except KeyError:
            self.terminal.error_message(
                f"Invalid register '{dest}' in DEC operation.")
            self.terminal.info_message(
                "TIP: Ensure the operand is a valid register.")

    @dispatch(list)
    def asm_shl(self, operands: list) -> int:
        """
        Executes the SHL instruction, performing a bitwise shift left on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None

        Example:
            [C]=> p mov ax,1
            Register Decimal    Hexadecimal  Binary            
            --------------------------------------------------
            AX       1          0x0001       0000000000000001  
            --------------------------------------------------
            [C]=> p shl ax
            Register Decimal    Hexadecimal  Binary            
            --------------------------------------------------
            AX       2          0x0002       0000000000000010  
            --------------------------------------------------
            [C]=> p shl ax
            Register Decimal    Hexadecimal  Binary            
            --------------------------------------------------
            AX       4          0x0004       0000000000000100  
            --------------------------------------------------            
        """

        (dst,) = operands
        dst = dst.strip().upper()

        val = self.register_collection.get(dst)
        carry = bool((val >> 15) & 0x1)           # bit que sale
        res = (val << 1) & 0xFFFF

        self.register_collection.set(dst, res)
        self.register_collection.update_flags(
            res, operation='SHL', carry=carry)
        return res

    @dispatch(list)
    def asm_shr(self, operands: list) -> None:
        """
        Executes the SHR instruction, performing a bitwise shift right on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        (dst,) = operands
        dst = dst.strip().upper()

        val = self.register_collection.get(dst)
        carry = bool(val & 0x1)                   # bit que sale
        res = (val >> 1) & 0x7FFF                 # relleno con 0

        self.register_collection.set(dst, res)
        self.register_collection.update_flags(
            res, operation='SHR', carry=carry)
        return res

    @dispatch(list)
    def asm_rol(self, operands: list) -> None:
        """
        Executes the ROL instruction, performing a bitwise rotate left on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        (dst,) = operands
        dst = dst.strip().upper()

        val = self.register_collection.get(dst)
        carry = bool((val >> 15) & 0x1)
        res = ((val << 1) & 0xFFFF) | (1 if carry else 0)

        self.register_collection.set(dst, res)
        self.register_collection.update_flags(
            res, operation='ROL', carry=carry)
        return res

    @dispatch(list)
    def asm_ror(self, operands: list) -> None:
        """
        Executes the ROR instruction, performing a bitwise rotate right on a register.

        Args:
            operands (list): List of operands (destination).

        Returns:
            None
        """
        (dst,) = operands
        dst = dst.strip().upper()

        val = self.register_collection.get(dst)
        carry = bool(val & 0x1)
        res = ((val >> 1) | ((val & 0x1) << 15)) & 0xFFFF

        self.register_collection.set(dst, res)
        self.register_collection.update_flags(
            res, operation='ROR', carry=carry)
        return res

    def assemble(self, asm_code: str, memory: Memory) -> List[int]:
        """
        Ensambla un bloque multilínea usando parse(..., dry_run=True) para tokenizar
        y luego codifica a bytes (subset educativo).
        """
        machine_code: List[int] = []
        lines = asm_code.strip().splitlines()

        for line_num, raw in enumerate(lines, 1):
            # quitar comentarios y espacios
            line = raw.split(';', 1)[0].strip()
            if not line:
                continue
            try:
                parsed = self.parse(line, memory, dry_run=True)
                if not parsed:
                    continue
                opcode = parsed['opcode']
                operands = parsed['operands']

                # Reutilizamos el codificador educativo por línea
                mnemonic = opcode + \
                    ((" " + ", ".join(operands)) if operands else "")
                bytes_line = self.assemble_line(mnemonic)
                machine_code.extend(bytes_line)

            except Exception as e:
                self.terminal.error_message(
                    f"assemble(): ERROR en línea {line_num}: {e}")
                # seguimos con el resto
                continue

        return machine_code

    def execute_and_print(self, instruction: str, memory: Memory) -> None:
        """
        Executes an assembly instruction and shows only the registers that changed.

        Args:
            instruction (str): Assembly instruction as a text string.

        Returns:
            None
        """        # Ejecuta la instrucción y maneja errores
        # try:
        self.parse(instruction, memory)
        self.register_collection.print_changed_registers()
        # except Exception as e:
        # self.terminal.error_message(f"execute_and_print(): ERROR: Execution failed for instruction '{instruction}'. Details: {e}")


class CpuX8086():
    """
    Class emulating a 8086 CPU.
    """

    def __init__(self) -> None:
        self.instruction_parser = InstructionParser()
        self.instructions_set = self.instruction_parser.supported_instructions
        self.register_set = self.instruction_parser.supported_registers
        self.terminal = Terminal()

    def parse_instruction(self, cmd: str, memory: Memory) -> None:
        """Parse the assembler instructions affecting the registers if necesary.


        Parameters:
            cmd {str}: Assembler instruction.


        Returns:
            None.

        """
        self.instruction_parser.execute_and_print(cmd, memory)

    #  https://www.geeksforgeeks.org/python-program-to-add-two-binary-numbers/
    def _find_matches(self, d: Dict[str, str], item: str):
        """

        Parameters:
            d {str}: Regex Dictionary
            item (str): Item to be look for.

        Returns:
            Dict[str]: Item found, or None if not.

        """
        for k in d:
            if re.match(k, item):
                return d[k]

        return None

    def _16to8(self, hl: int) -> Tuple[int]:
        """Decode a 16-bit number in 2 8-bit numbers (high, low)."""
        h = (hl >> 8) & 0xFF
        l = hl & 0xFF
        return h, l

    @staticmethod
    def _not_yet():
        print("This part of the CPU hasn't been implemented yet. =)")

    @dispatch(int)
    def get_bin(self, x: int) -> str:
        """Convert any integer into n bit binary format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 16 bit binary as string.
        """
        return format(x, '016b')

    @dispatch(int)
    def get_hex(self, x: int) -> str:
        """Convert any integer into 16 bit hexadecimal format.

        Parameters:
            x (int): The integer to be converted.

        Returns:
            str: 16 bit hexadecimal as string.
        """

        return format(x, '04X')

    def assemble(self, memory: Memory, code: str) -> str:
        """
        Assemble the code into machine code.

        Args:
            memory (Memory): Memory object class.
            code (str): Code to be assembled.

        Returns:
            str: Machine code.
        """

        machine_code = self.instruction_parser.assemble(code, memory)
        if len(machine_code) > 0:
            self.terminal.info_message(Icons.MACHINE_CODE.value, ','.join(
                format(byte, '02X') for byte in machine_code))
            print("\n")
            memory.offset_cursor += len(machine_code)

        return machine_code

    def print_registers(self) -> None:
        """ Print the CPU registers and it's value."""
        self.instruction_parser.register_collection.print_registers()

    def move(self, memory: Memory, from_begin: int, from_end: int, destination: int) -> bool:
        """Copy a memory region to other memory region.

        Parameters:
            memory (Memory): A Memory class object.
            from_begin (int): Source's begin.
            from_end (int): Source's end.
            destination (int): Destination's begin.

        Returns:
            bool: Operation result.
        """

        if destination > from_end:
            for source in range(from_begin, from_end):
                dist_pointer = from_begin \
                    if destination + source == from_begin else destination + source - from_begin
                memory.poke(memory.active_page, dist_pointer,
                            memory.peek(memory.active_page, source))
            self.terminal.success_message(
                f"{from_end - from_begin} byte/s copied.")
            return True

        self.terminal.error_message("Invalid value.")
        return False

    def fill(self, memory: Memory, start: int, end: int, pattern: str) -> bool:
        """Fill a memory region with a specified pattern.

        Parameters:
            memory (Memory): A Memory class object.
            start (int): Source's begin.
            end (int): Source's end.
            pattern (str): Pattern.

        Returns:
            bool: Operation result. Always true.
        """
        cursor = 0
        for idx in range(start, end):
            memory.poke(memory.active_page, idx, ord(pattern[cursor]))
            cursor += 1
            if cursor > len(pattern) - 1:
                cursor = 0

        return True

    def search(self, memory: Memory, start: int, pattern: str) -> List[str]:
        """Search a pattern in the memory. Staring from <start> to the end of the page.

        Parameters:
            memory (Memory): Memory class object.
            start (int): Starting point from the search.
            pattern (str): Pattern to search for.

        Returns:
            [str]
        """
        found_list = []
        pointer = start
        while pointer < memory._offsets:
            idx = 0

            # Did I find the first char of the pattern? If so, let's search for the rest
            if memory.peek(memory.active_page, pointer) == ord(pattern[idx]):
                pointer_aux = pointer
                while idx < len(pattern) and pointer_aux < memory._offsets and \
                        memory.peek(memory.active_page, pointer_aux) == ord(pattern[idx]):
                    idx += 1
                    pointer_aux += 1

                if pointer_aux - pointer == len(pattern):
                    found_list.append(
                        f"{'%04X' % memory.active_page}:{'%04X' % pointer}")

            pointer += 1

        return found_list

    def load_into(self, memory: Memory, start: int, text: str) -> None:
        """
        Load a text into memory, starting from an address.

        Args:
            memory (Memory): Memory object class.
            start (int): Address memory where to begin.
            text (str): Text to be load into.

        Returns:
            None
        """
        for idx in range(0, len(text) - 1):
            memory.poke(memory.active_page, start + idx, ord(text[idx]))

    def compare(self, memory: Memory, cfrom: int, cend: int, cto: int) -> List[str]:
        """
        Compares two memory regions.

        Args:
            memory (Memory): Memory object class.
            cfrom (int): Source address memory where to start.
            cend (int): Source address memory where to end.
            cto (int): Destination address memory.

        Returns:
            [str]: The differences between regions.
        """
        diffs = []

        for a in range(cfrom, cend):
            org = memory.peek(memory.active_page, a)
            dist_pointer = cfrom if cto + a == cfrom else cto + a - cfrom - 1

            dist = memory.peek(memory.active_page, dist_pointer)
            if org != dist:
                diffs.append('%04X' % memory.active_page + ":" + '%04X' % a + " " +
                             '%02X' % org + " " + '%02X' % dist + " " +
                             '%04X' % memory.active_page + ":" + '%04X' % dist_pointer)

        return diffs

    def cat(self, disk: Disk, addrb: int, addrn: int) -> None:
        """
        Shows the content of the vdisk region.

        Args:
            disk: A Disk class type object.
            addrb: Start address.
            addrn: End address.

        Returns:

        """
        bytes_per_row = int("F", 16)
        pointer = 0
        ascvisual = ""

        if addrn - addrb < bytes_per_row:  # One single row
            print(f"{'%06X' % (pointer + addrb)} ", end="", flush=True)
            for address in range(addrb, addrn):
                byte = disk.read(pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                self.terminal.success_message(f"{peek} ", end="", flush=True)

            self.terminal.success_message(
                " " * ((bytes_per_row - pointer) * 3) + ascvisual)
        else:  # two or more rows
            while pointer + addrb < addrn:
                if pointer % bytes_per_row == 0:
                    self.terminal.success_message(
                        " " * ((bytes_per_row - pointer) * 3) + ascvisual)
                    ascvisual = ""
                    self.terminal.success_message(
                        f"{'%06X' % (pointer + addrb)} ", end="", flush=True)

                byte = disk.read(pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                self.terminal.success_message(f"{peek} ", end="", flush=True)
                pointer += 1

        print("")

    def display(self, memory: Memory, addrb: int, addrn: int) -> None:
        """
        Displays a memory region.

        Args:
            memory: A Memory class type object.
            addrb: Start address.
            addrn: End address.

        Returns:
            None.
        """
        # Usar entero para Memory.peek(...)
        page = memory.active_page
        bytes_per_row = int("F", 16)
        pointer = 0
        ascvisual = ""

        if addrn - addrb < bytes_per_row:  # One single row
            self.terminal.success_message(
                f"{memory.active_page:04X}:{(pointer + addrb):04X} ", end="", flush=True)
            for _ in range(addrb, addrn):
                byte = memory.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                self.terminal.info_message(f"{peek} ", "", True)

            self.terminal.default_message(
                " " * ((bytes_per_row - pointer) * 3) + ascvisual)
        else:  # two or more rows
            while pointer + addrb < addrn:
                if pointer % bytes_per_row == 0:
                    print(" " * ((bytes_per_row - pointer) * 3) + ascvisual)
                    ascvisual = ""
                    self.terminal.success_message(
                        f"{memory.active_page:04X}:{(pointer + addrb):04X} ", end="")
                byte = memory.peek(page, pointer + addrb)
                peek = "%02X" % byte
                ascvisual += chr(byte) if chr(byte).isprintable() else "."
                self.terminal.info_message(f"{peek} ", "", True)
                pointer += 1

        print("")

    def write_to_vdisk(self, memory: Memory, disk: Disk, address: int, firstsector: int, number: int) -> None:
        """
        Writes onto vdisk a memory block.

        Args:
            memory (Memory): A Memory type class object.
            disk (Disk): A Disk type class object.
            address (int): Source memory address.
            firstsector (int): Destination sector address.
            number (int): Number of bytes to be copied.

        Returns:
            None.
        """
        for i in range(0, number - 1):
            print("Writing to vdisk...", firstsector +
                  i, memory.peek(address + i))
            disk.write(firstsector+i, memory.peek(address + i))

    def read_from_vdisk(self, memory: Memory, disk: Disk, address: int, firstsector: int, number: int) -> None:
        """
        Loads into memory a vdisk block.

        Args:
            memory (Memory): A Memory type class object.
            disk (Disk): A Disk type class object.
            address (int): Destination memory address.
            firstsector (int): Source sector address.
            number (int): Number of bytes to be copied.

        Returns:
            None.
        """
        for i in range(0, number - 1):
            memory.poke(memory.active_page, address,
                        disk.read(firstsector + i))
