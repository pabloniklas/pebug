"""_summary_
Unit tests for the RegisterSet class from the modules.CpuX8086 module.

Test Cases:
- test_get_and_set_register: Verifies setting and retrieving a register value.
- test_update_flags: Checks correct update of Zero Flag (ZF), Sign Flag (SF), and Parity Flag (PF) after an operation.
- test_set_upper_and_lower: Tests setting the upper and lower bytes of a register value.

Each test ensures the RegisterSet behaves as expected for basic register and flag operations.
"""
import unittest
from modules.CpuX8086 import RegisterSet

class TestRegisterSet(unittest.TestCase):
    """
    Unit tests for the RegisterSet class.

    Test Cases:
    - test_get_and_set_register: Verifies that setting and getting a register value works as expected.
    - test_update_flags: Checks that the update_flags method correctly updates the Zero Flag (ZF), Sign Flag (SF), and Parity Flag (PF) based on the provided value.
    - test_set_upper_and_lower: Ensures that setting the upper or lower byte of a register value works correctly via set_register_upper and set_register_lower methods.

    setUp:
    - Initializes a new RegisterSet instance before each test.
    """
    def setUp(self):
        self.regs = RegisterSet()

    def test_get_and_set_register(self):
        """
        Tests that the set and get methods for registers work correctly by setting the value of the "AX" register and verifying that the retrieved value matches the expected result.
        """
        self.regs.set("AX", 0x1234)
        self.assertEqual(self.regs.get("AX"), 0x1234)

    def test_update_flags(self):
        """
        Test the update_flags method to ensure that the Zero Flag (ZF), Sign Flag (SF), and Parity Flag (PF)
        are correctly set when the input value is 0.

        - Verifies that ZF is set to 1 when the value is zero.
        - Verifies that SF is set to 0 when the value is zero.
        - Verifies that PF is set to 1 when the value is zero.
        """
        self.regs.update_flags(0)
        self.assertEqual(self.regs.flags["ZF"], 1)
        self.assertEqual(self.regs.flags["SF"], 0)
        self.assertEqual(self.regs.flags["PF"], 1)

    def test_set_upper_and_lower(self):
        """
        Tests the set_register_upper and set_register_lower methods to ensure they correctly set the upper and lower bytes of a register value.

        - Verifies that set_register_upper replaces the upper byte of a 16-bit register value with the specified value.
        - Verifies that set_register_lower replaces the lower byte of a 16-bit register value with the specified value.
        """
        self.assertEqual(self.regs.set_register_upper(0x00FF, 0x12), 0x12FF)
        self.assertEqual(self.regs.set_register_lower(0xFF00, 0x34), 0xFF34)

if __name__ == '__main__':
    unittest.main()