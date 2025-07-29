"""
        Unit tests for the InstructionParser class.
        This module contains test cases for the asm_add, asm_sub, asm_mov, and asm_shl methods,
        which handle the encoding of x86 assembly instructions into machine code.
"""

import unittest
from modules.CpuX8086 import InstructionParser
from modules.Memory import Memory


class TestAsmAdd(unittest.TestCase):
    """
    Unit tests for the 'asm_add' method of the InstructionParser class.

    This test suite verifies the correct encoding of the ADD instruction for various operand combinations,
    including immediate values (both decimal and hexadecimal), register-to-register operations, and error handling
    for invalid operands or registers.

    Test cases:
    - test_add_ax_imm16_decimal: Tests ADD AX, imm16 with a decimal immediate.
    - test_add_ax_imm16_hex: Tests ADD AX, imm16 with a hexadecimal immediate.
    - test_add_bx_imm16_decimal: Tests ADD BX, imm16 with a decimal immediate.
    - test_add_cx_imm16_hex: Tests ADD CX, imm16 with a hexadecimal immediate.
    - test_add_reg_reg: Tests ADD reg16, reg16 (register to register).
    - test_add_invalid_registers: Ensures ValueError is raised for invalid register names.
    - test_add_invalid_operands: Ensures ValueError is raised for invalid operand combinations.
    """

    def setUp(self):
        self.parser = InstructionParser()
        self.memory = Memory()

    def test_add_ax_imm16_decimal(self):
        """
        Tests that the asm_add method correctly encodes the 'ADD AX, imm16' instruction
        when given a decimal immediate value. Verifies that adding 100 to AX produces
        the expected machine code bytes [0x05, 0x64, 0x00], where 0x64 is the little-endian
        representation of 100.
        """
        code = self.parser.asm_add(["AX", "100"])
        self.assertEqual(code, [0x05, 0x64, 0x00])  # 0x64 = 100

    def test_add_ax_imm16_hex(self):
        """
        Tests the 'asm_add' method for the case where the ADD instruction adds a 16-bit immediate hexadecimal value (0x1234) to the AX register.
        Asserts that the generated machine code matches the expected opcode and operand bytes: [0x05, 0x34, 0x12].
        """
        code = self.parser.asm_add(["AX", "0x1234"])
        self.assertEqual(code, [0x05, 0x34, 0x12])

    def test_add_bx_imm16_decimal(self):
        """
        Test that the assembler correctly encodes the instruction 'ADD BX, 200' 
        where the immediate value is given in decimal (200). 
        Verifies that the resulting machine code matches the expected byte sequence [0x81, 0xC3, 0xC8, 0x00],
        where 0xC8 is the little-endian encoding of 200.
        """
        code = self.parser.asm_add(["BX", "200"])
        self.assertEqual(code, [0x81, 0xC3, 0xC8, 0x00])  # 0xC8 = 200

    def test_add_cx_imm16_hex(self):
        """
        Tests the asm_add method for adding a 16-bit immediate hexadecimal value to the CX register.

        This test verifies that the assembler correctly encodes the instruction for adding the immediate
        value 0x01F4 to the CX register, and that the resulting machine code matches the expected byte sequence.

        Asserts:
            The output machine code should be [0x81, 0xC1, 0xF4, 0x01].
        """
        code = self.parser.asm_add(["CX", "0x01F4"])
        self.assertEqual(code, [0x81, 0xC1, 0xF4, 0x01])

    def test_add_reg_reg(self):
        """
        Tests the asm_add method for the case where both operands are registers.
        Verifies that adding the contents of register CX to register BX produces the correct machine code [0x01, 0xCB].
        """
        code = self.parser.asm_add(["BX", "CX"])
        self.assertEqual(code, [0x01, 0xCB])  # BX += CX

    def test_add_invalid_registers(self):
        """
        Test that asm_add raises a ValueError when provided with invalid register names.
        This test ensures that the parser correctly identifies and rejects invalid register inputs,
        such as non-existent register names or improperly formatted register values.
        """
        with self.assertRaises(ValueError):
            self.parser.asm_add(["FOO", "100"])

    def test_add_invalid_operands(self):
        """
        Test that the asm_add method raises a ValueError when provided with invalid operands.
        """
        with self.assertRaises(ValueError):
            self.parser.asm_add(["AX", "BL"])

class TestAsmSub(unittest.TestCase):
    """
    Unit tests for the asm_sub method of the InstructionParser class.

    This test suite verifies the correct encoding of the SUB instruction for various operand combinations,
    including immediate values (both decimal and hexadecimal) and register-to-register operations.
    It also checks for proper error handling when invalid registers or operands are provided.

    Test Cases:
    - test_sub_ax_imm16_decimal: Tests SUB AX, imm16 with a decimal immediate.
    - test_sub_ax_imm16_hex: Tests SUB AX, imm16 with a hexadecimal immediate.
    - test_sub_bx_imm16_decimal: Tests SUB BX, imm16 with a decimal immediate.
    - test_sub_cx_imm16_hex: Tests SUB CX, imm16 with a hexadecimal immediate.
    - test_sub_reg_reg: Tests SUB reg16, reg16 (BX, CX).
    - test_sub_invalid_registers: Ensures ValueError is raised for invalid register names.
    - test_sub_invalid_operands: Ensures ValueError is raised for invalid operand combinations.
    """

    def setUp(self):
        self.parser = InstructionParser()
        self.memory = Memory()

    # Tests para asm_sub()
    def test_sub_ax_imm16_decimal(self):
        """
        Tests that the asm_sub method correctly encodes the 'SUB AX, imm16' instruction with a decimal immediate value.
        Verifies that the resulting machine code matches the expected byte sequence for 'SUB AX, 100'.
        """
        code = self.parser.asm_sub(["AX", "100"])
        self.assertEqual(code, [0x2D, 0x64, 0x00])

    def test_sub_ax_imm16_hex(self):
        """
        Tests the 'asm_sub' method for the 'SUB AX, imm16' instruction with a hexadecimal immediate value.
        Verifies that assembling 'SUB AX, 0x1234' produces the correct opcode and operand bytes: [0x2D, 0x34, 0x12].
        """
        code = self.parser.asm_sub(["AX", "0x1234"])
        self.assertEqual(code, [0x2D, 0x34, 0x12])

    def test_sub_bx_imm16_decimal(self):
        """
        Test that the assembler correctly encodes the instruction 'SUB BX, 200' using a 16-bit immediate value.
        Verifies that the output machine code matches the expected byte sequence [0x81, 0xEB, 0xC8, 0x00].
        """
        code = self.parser.asm_sub(["BX", "200"])
        self.assertEqual(code, [0x81, 0xEB, 0xC8, 0x00])

    def test_sub_cx_imm16_hex(self):
        """
        Tests the asm_sub method for subtracting a 16-bit immediate hexadecimal value (0x01F4) from the CX register.
        
        Verifies that the generated machine code matches the expected opcode sequence for the instruction:
        SUB CX, 0x01F4

        Expected output: [0x81, 0xE9, 0xF4, 0x01]
        """
        code = self.parser.asm_sub(["CX", "0x01F4"])
        self.assertEqual(code, [0x81, 0xE9, 0xF4, 0x01])

    def test_sub_reg_reg(self):
        """
        Tests that the asm_sub method correctly encodes the SUB instruction with two register operands.
        Verifies that subtracting the value in register CX from BX produces the expected machine code [0x29, 0xCB].
        """
        code = self.parser.asm_sub(["BX", "CX"])
        self.assertEqual(code, [0x29, 0xCB])

    def test_sub_invalid_registers(self):
        """
        Test that the asm_sub method raises a ValueError when provided with invalid register names.
        """
        with self.assertRaises(ValueError):
            self.parser.asm_sub(["FOO", "100"])

    def test_sub_invalid_operands(self):
        """
        Test that the asm_sub method raises a ValueError when provided with invalid operands.
        """
        with self.assertRaises(ValueError):
            self.parser.asm_sub(["AX", "BL"])


class TestAsmMov(unittest.TestCase):
    """
    Unit tests for the asm_mov() method of the InstructionParser class.

    This test suite verifies the correct encoding of x86 MOV instructions
    for various operand types and error conditions.

    Test Cases:
    - test_mov_reg_imm16_decimal: Tests MOV from immediate decimal to register.
    - test_mov_reg_imm16_hex: Tests MOV from immediate hexadecimal to register.
    - test_mov_reg_reg: Tests MOV from register to register.
    - test_mov_invalid_registers: Ensures ValueError is raised for invalid register names.
    - test_mov_invalid_operands: Ensures ValueError is raised for invalid operand combinations.
    """

    def setUp(self):
        self.parser = InstructionParser()
        self.memory = Memory()

    # Tests para asm_mov()
    def test_mov_reg_imm16_decimal(self):
        """
        Tests that the asm_mov method correctly encodes a MOV instruction that moves a 16-bit immediate decimal value (100) into the AX register.
        Verifies that the resulting machine code matches the expected byte sequence [0xB8, 0x64, 0x00].
        """
        code = self.parser.asm_mov(["AX", "100"])
        self.assertEqual(code, [0xB8, 0x64, 0x00])

    def test_mov_reg_imm16_hex(self):
        """
        Tests the 'asm_mov' method for moving a 16-bit immediate hexadecimal value into a register.
        Verifies that assembling 'MOV BX, 0x1234' produces the correct machine code bytes [0xBB, 0x34, 0x12].
        """
        code = self.parser.asm_mov(["BX", "0x1234"])
        self.assertEqual(code, [0xBB, 0x34, 0x12])

    def test_mov_reg_reg(self):
        """
        Test that the asm_mov method correctly encodes a MOV instruction from one register to another.
        Verifies that moving the value from register DX to CX produces the expected machine code [0x89, 0xD1].
        """
        code = self.parser.asm_mov(["CX", "DX"])
        self.assertEqual(code, [0x89, 0xD1])

    def test_mov_invalid_registers(self):
        """
        Test that asm_mov raises a ValueError when provided with invalid register names.
        """
        with self.assertRaises(ValueError):
            self.parser.asm_mov(["FOO", "100"])

    def test_mov_invalid_operands(self):
        """
        Test that the asm_mov method raises a ValueError when provided with invalid operands.

        This test verifies that attempting to move data between incompatible registers
        (e.g., "AX" and "BL") results in a ValueError, ensuring operand validation is enforced.
        """
        with self.assertRaises(ValueError):
            self.parser.asm_mov(["AX", "BL"])


class TestAsmShl(unittest.TestCase):
    """
    Unit tests for the asm_shl() method of the InstructionParser class.

    This test case verifies the correct encoding of the SHL (shift left) assembly instruction for different operands.

    Test Cases:
    - test_shl_reg: Ensures that the SHL instruction is correctly encoded when a valid register (e.g., "BX") is provided.
    - test_shl_invalid_register: Ensures that a ValueError is raised when an invalid register name is provided as an operand.
    """

    def setUp(self):
        self.parser = InstructionParser()
        self.memory = Memory()

    # Tests para asm_shl()
    def test_shl_reg(self):
        """
        Tests that the asm_shl method correctly generates the machine code for the SHL instruction with the BX register.
        Asserts that the output matches the expected opcode sequence [0xD1, 0xE3].
        """
        code = self.parser.asm_shl(["BX"])
        self.assertEqual(code, [0xD1, 0xE3])

    def test_shl_invalid_register(self):
        """
        Test that asm_shl raises a ValueError when provided with an invalid register name.
        """
        with self.assertRaises(ValueError):
            self.parser.asm_shl(["FOO"])