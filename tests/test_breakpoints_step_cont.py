import unittest
from modules.CpuX8086 import CpuX8086
from modules.Memory import Memory

class TestBreakpointsStepCont(unittest.TestCase):
    def setUp(self):
        self.cpu = CpuX8086()
        self.ip = self.cpu.instruction_parser
        self.mem = Memory()

    def test_breakpoints_step_cont(self):
        prog = [
            "MOV AX, 0x0001",
            "ADD AX, 2",
            "EMIT:",
            "INC AX",
            "DEC AX",
        ]

        self.ip.load_program(prog, base_addr=0x0100)

        logs = []
        self.ip.enable_trace(True, out=lambda s: logs.append(s))

        # Breakpoint por label
        self.ip.add_breakpoint("EMIT")

        self.assertEqual(self.ip.step(self.mem), prog[0])
        self.assertEqual(self.ip.step(self.mem), prog[1])

        self.ip.cont(self.mem)
        self.assertTrue(any(l.startswith("[break]") for l in logs), "No se reportó el breakpoint por label")

        # Breakpoint por dirección (cada línea cuenta 1)
        self.ip.remove_breakpoint("EMIT")
        self.ip.add_breakpoint(0x0104)
        self.ip.cont(self.mem)
        self.assertGreaterEqual(len([l for l in logs if l.startswith("[break]")]), 2, "No se reportó el bp por dirección")

if __name__ == "__main__":
    unittest.main()
