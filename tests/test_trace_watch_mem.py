import unittest
from modules.CpuX8086 import CpuX8086
from modules.Memory import Memory

class TestTraceWatchMem(unittest.TestCase):
    def setUp(self):
        self.cpu = CpuX8086()
        self.ip = self.cpu.instruction_parser
        self.mem = Memory()

        # Terminal collector para no imprimir en stdout
        self.trace_lines = []
        class _T:
            def __init__(self, sink): self._sink = sink
            def default_message(self, msg, end="\n"):
                self._sink.append(str(msg) + ("" if end == "" else end))
        self.term_out = []
        self.ip.terminal = _T(self.term_out)

    def _write_dos_string(self, page: int, addr: int, text: str):
        for i, ch in enumerate(text + "$"):
            self.mem.poke(page, addr + i, ord(ch))

    def test_trace_watch_and_mem_access(self):
        PAGE = self.mem.active_page
        DX = 0x0200
        self._write_dos_string(PAGE, DX, "HOLA")

        prog = [
            "MOV AX, 0x0001",
            "ADD AX, 1",
            "SHL AX",
            "MOV DS, 0x0000",
            f"MOV DX, 0x{DX:04X}",
            "MOV AX, 0x0900",  # AH=09h
            "INT 0x21",
        ]

        self.ip.enable_trace(True, out=lambda s: self.trace_lines.append(s))
        for line in prog:
            self.ip.parse(line, self.mem)

        add_lines = [l for l in self.trace_lines if l.startswith("ADD AX, 1")]
        self.assertTrue(add_lines, "No se registró traza para ADD AX, 1")
        self.assertIn("bytes(pseudo):", add_lines[0])
        self.assertIn("regsΔ:", add_lines[0])
        self.assertIn("flagsΔ:", add_lines[0])

        int_lines = [l for l in self.trace_lines if l.startswith("INT 0x21")]
        self.assertTrue(int_lines, "No se registró traza para INT 0x21")
        self.assertIn("mem: ", int_lines[0], "La traza de INT no muestra accesos a memoria")
        self.assertIn(f"R[p{PAGE}:{DX:04X}]", int_lines[0], "No aparecen lecturas DS:DX")

        # Watches
        self.trace_lines.clear()
        self.ip.clear_watches()
        self.ip.add_watch("AX")
        self.ip.add_watch("FLAGS.CF")

        self.ip.parse("MOV AX, 0x0003", self.mem)  # baseline
        self.ip.parse("ADD AX, 1", self.mem)
        self.assertTrue(any(l.startswith("[watch] AX:") for l in self.trace_lines), "No se registró watch AX")

        self.ip.parse("MOV AX, 0x8000", self.mem)
        self.ip.parse("SHL AX", self.mem)
        self.assertTrue(any(l.startswith("[watch] FLAGS.CF:") for l in self.trace_lines), "No se registró watch CF")

if __name__ == "__main__":
    unittest.main()
