"""_summary_
Unit tests for the CpuX8086 class, simulating 8086 CPU instructions.

This test suite verifies the correct parsing and execution of various 8086 assembly instructions
by the CpuX8086 emulator, including MOV, ADD, SUB, SHL, SHR, AND, OR, XOR, ROL, and ROR.
Each test initializes a fresh CPU and memory instance, executes a sequence of instructions,
and asserts that the target register contains the expected value after execution.

Tested instructions and behaviors:
- MOV: Move immediate values into registers.
- ADD: Add immediate values to registers.
- SUB: Subtract immediate values from registers.
- SHL: Shift register values left by one bit.
- SHR: Shift register values right by one bit.
- AND: Bitwise AND between register and immediate value.
- OR: Bitwise OR between register and immediate value.
- XOR: Bitwise XOR between register and immediate value.
- ROL: Rotate register value left by one bit.
- ROR: Rotate register value right by one bit.

Each test ensures that the CpuX8086 instruction parser and execution logic
correctly update the register values according to the semantics of the 8086 instruction set.
"""

import unittest
from modules.CpuX8086 import CpuX8086
from modules.Memory import Memory
class TestCpuX8086(unittest.TestCase):
    """Test suite for the CpuX8086 class.

    Args:
        unittest (module): The unittest module for creating and running tests.
    """
    def setUp(self):
        self.cpu = CpuX8086()
        self.memory = Memory()

    def test_mov_instruction(self):
        """
        Tests the MOV instruction by parsing "MOV AX, 5" and asserting that the AX register is set to 5.
        """
        self.cpu.parse_instruction("MOV AX, 5", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("AX"), 5)

    def test_add_instruction(self):
        """
        Tests the addition instruction by first moving the value 2 into the AX register,
        then adding 3 to AX, and finally asserting that the AX register contains the expected result (5).
        """
        self.cpu.parse_instruction("MOV AX, 2", self.memory)
        self.cpu.parse_instruction("ADD AX, 3", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("AX"), 5)

    def test_sub_instruction(self):
        """
        Tests the SUB instruction by first moving the value 10 into the BX register,
        then subtracting 4 from BX, and finally asserting that the BX register contains 6.
        """
        self.cpu.parse_instruction("MOV BX, 10", self.memory)
        self.cpu.parse_instruction("SUB BX, 4", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("BX"), 6)

    def test_shl_instruction(self):
        """
        Tests the SHL (shift left) instruction on the CX register.

        This test performs the following steps:
        1. Moves the value 1 into the CX register.
        2. Executes the SHL instruction on CX, which should shift the value left by one bit (equivalent to multiplying by 2).
        3. Asserts that the value in the CX register is now 2.

        Ensures that the SHL instruction is correctly implemented for the CX register.
        """
        self.cpu.parse_instruction("MOV CX, 1", self.memory)
        self.cpu.parse_instruction("SHL CX", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("CX"), 2)

    def test_and_instruction(self):
        """
        Tests the 'AND' instruction by first moving the value 0x0F0F into the AX register,
        then performing a bitwise AND operation with 0x00FF. Asserts that the result in AX
        is 0x000F, verifying correct instruction parsing and execution.
        """
        self.cpu.parse_instruction("MOV AX, 0x0F0F", self.memory)
        self.cpu.parse_instruction("AND AX, 0x00FF", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("AX"), 0x000F)

    def test_or_instruction(self):
        """
        Tests the OR instruction by first moving the value 0xF000 into the BX register,
        then performing a bitwise OR with 0x00FF. Asserts that the resulting value in BX
        is 0xF0FF, verifying correct execution of the OR operation.
        """
        self.cpu.parse_instruction("MOV BX, 0xF000", self.memory)
        self.cpu.parse_instruction("OR BX, 0x00FF", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("BX"), 0xF0FF)

    def test_xor_instruction(self):
        """
        Tests the XOR instruction by first setting the CX register to 0xFFFF and then performing an XOR operation with 0x0F0F.
        Asserts that the resulting value in the CX register is 0xF0F0.
        """
        self.cpu.parse_instruction("MOV CX, 0xFFFF", self.memory)
        self.cpu.parse_instruction("XOR CX, 0x0F0F", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("CX"), 0xF0F0)

    def test_shr_instruction(self):
        """
        Tests the SHR (shift right) instruction by moving the value 0x0004 into the DX register,
        executing the SHR DX instruction, and asserting that the result in DX is 0x0002.
        """
        self.cpu.parse_instruction("MOV DX, 0x0004", self.memory)
        self.cpu.parse_instruction("SHR DX", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("DX"), 0x0002)

    def test_rol_instruction(self):
        """
        Tests the ROL (rotate left) instruction by first moving the value 0x8001 into the AX register,
        then performing a rotate left operation on AX. Asserts that the resulting value in AX is 0x0003,
        verifying correct implementation of the ROL instruction.
        """
        self.cpu.parse_instruction("MOV AX, 0x8001", self.memory)
        self.cpu.parse_instruction("ROL AX", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("AX"), 0x0003)

    def test_ror_instruction(self):
        """
        Tests the 'ROR' (rotate right) instruction for the CPU emulator.

        This test sets the BX register to 0x0001, performs a rotate right operation,
        and asserts that the result is 0x8000, verifying correct bit rotation behavior.
        """
        self.cpu.parse_instruction("MOV BX, 0x0001", self.memory)
        self.cpu.parse_instruction("ROR BX", self.memory)
        self.assertEqual(self.cpu.instruction_parser.register_collection.get("BX"), 0x8000)

if __name__ == '__main__':
    unittest.main()
