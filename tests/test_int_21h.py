import unittest
from modules.CpuX8086 import CpuX8086
from modules.Memory import Memory

class TestINT21H(unittest.TestCase):
    def setUp(self):
        self.cpu = CpuX8086()
        self.memory = Memory()
        self.memory.active_page = 0
        self.regs = self.cpu.instruction_parser.register_collection

    def test_service_09_print_string(self):
        # Configurar cadena "HELLO$" en memoria
        string = "HELLO$"
        segment = 0x0F00  # da 0x0F00 << 4 = 0xF000, dentro del rango
        offset = 0x0010
        address = (segment << 4) + offset
        for i, char in enumerate(string):
            self.memory.poke(0, address + i, ord(char))

        self.regs.set("AX", 0x0900)  # AH = 09h
        self.regs.set("DS", segment)
        self.regs.set("DX", offset)

        # No se captura la salida, pero se asegura de no lanzar errores
        self.cpu.parse_instruction("INT 0x21", self.memory)

    def test_service_4c_exit(self):
        self.regs.set("AX", 0x4C00)  # AH = 4Ch
        with self.assertRaises(SystemExit) as cm:
            self.cpu.parse_instruction("INT 0x21", self.memory)
        self.assertEqual(cm.exception.code, 0)

if __name__ == '__main__':
    unittest.main()
