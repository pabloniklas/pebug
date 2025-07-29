import unittest
from modules.CpuX8086 import CpuX8086
from modules.Memory import Memory

class TestCpuX8086(unittest.TestCase):
    def setUp(self):
        self.cpu = CpuX8086()
        self.memory = Memory()

    def test_mov_instruction(self):
        self.cpu.parse_instruction("MOV AX, 5", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("AX"), 5)

    def test_add_instruction(self):
        self.cpu.parse_instruction("MOV AX, 2", self.memory)
        self.cpu.parse_instruction("ADD AX, 3", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("AX"), 5)

    def test_sub_instruction(self):
        self.cpu.parse_instruction("MOV BX, 10", self.memory)
        self.cpu.parse_instruction("SUB BX, 4", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("BX"), 6)

    def test_shl_instruction(self):
        self.cpu.parse_instruction("MOV CX, 1", self.memory)
        self.cpu.parse_instruction("SHL CX", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("CX"), 2)

if __name__ == '__main__':
    unittest.main()
