import unittest
from modules.CpuX8086 import CpuX8086
from modules.Memory import Memory

class TestDisassembler(unittest.TestCase):
    def setUp(self):
        self.cpu = CpuX8086()
        self.ip = self.cpu.instruction_parser
        self.mem = Memory()

    def test_disassembler(self):
        prog = [
            "MOV AX, 0x0003",
            "ADD AX, 5",
            "MOV BX, AX",
            "INT 0x21",    # pseudo bytes: 0xCD 0x21
        ]
        self.ip.load_program(prog, base_addr=0x0100)

        listing = self.ip.disassemble_program()
        self.assertEqual(len(listing), len(prog), "Cantidad de líneas desensambladas incorrecta")
        self.assertTrue(any("bytes(pseudo)" in l for l in listing), "Falta bytes(pseudo)")

        mov_line = next((l for l in listing if l.startswith("0100: MOV AX, 0x0003")), None)
        self.assertIsNotNone(mov_line)
        self.assertIn("bytes(pseudo):", mov_line)

        int_line = next((l for l in listing if "INT 0x21" in l), None)
        self.assertIsNotNone(int_line)
        self.assertTrue(("CD 21" in int_line) or ("cd 21" in int_line) or ("CD 15" in int_line))

        one = self.ip.disassemble_line("ADD AX, 1", addr=0x0200)
        self.assertTrue(one.startswith("0200: ADD AX, 1"))
        self.assertIn("bytes(pseudo):", one)

if __name__ == "__main__":
    unittest.main()
