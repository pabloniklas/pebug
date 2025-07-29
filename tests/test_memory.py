"""_summary_
Unit tests for the Memory class in modules.Memory.

This test suite verifies the following behaviors:
- Correctly storing and retrieving integer values using poke and peek.
- Handling invalid memory addresses and values gracefully.
- Storing string values as their ASCII codes in consecutive memory locations.

Tested methods:
- poke(page, address, value): Writes a value (int or str) to a given page and address.
- peek(page, address): Reads the value at a given page and address.

Test cases:
- test_poke_and_peek_int: Verifies integer write/read operations.
- test_poke_invalid_value: Ensures invalid addresses and values are rejected.
- test_poke_string: Checks that strings are stored as ASCII codes in memory.
"""

import unittest
from modules.Memory import Memory

class TestMemory(unittest.TestCase):
    """
    Unit tests for the Memory class.

    Test Cases:
    - test_poke_and_peek_int: Verifies that an integer value can be stored and retrieved correctly at a valid address.
    - test_poke_invalid_value: Ensures that invalid addresses and values are correctly rejected by the poke method.
    - test_poke_string: Checks that a string can be stored starting at a given address, and that each character is stored as its ASCII value in consecutive addresses.
    """
    def setUp(self):
        self.mem = Memory()  # Crea una sola página: página 0

    def test_poke_and_peek_int(self):
        """
        Tests the 'poke' and 'peek' methods for integer values.

        This test verifies that:
        - The 'poke' method correctly writes an integer value (123) to a valid memory location (page 0, offset 100).
        - The method returns True to indicate a successful write.
        - The 'peek' method retrieves the same integer value (123) from the specified memory location.

        Assertions:
        - The result of 'poke' is True.
        - The value returned by 'peek' matches the value written.
        """
        result = self.mem.poke(0, 100, 123)  # Página 0, válida
        self.assertTrue(result)
        self.assertEqual(self.mem.peek(0, 100), 123)

    def test_poke_invalid_value(self):
        """
        Test that the `poke` method correctly handles invalid input values.

        This test verifies that:
        - Attempting to poke a value at an invalid memory address (e.g., 65536) returns False.
        - Attempting to poke an invalid value (e.g., 999) at a valid address returns False.
        """
        self.assertFalse(self.mem.poke(0, 65536, 255))  # Dirección inválida
        self.assertFalse(self.mem.poke(0, 0, 999))      # Valor inválido

    def test_poke_string(self):
        """
        Tests the `poke` method for writing a string to memory and verifies that each character is correctly stored at consecutive addresses.

        This test:
        - Writes the string "ABC" starting at address 10 on page 0 using `poke`.
        - Asserts that the operation returns True.
        - Checks that each character ('A', 'B', 'C') is stored at the correct memory locations by comparing the result of `peek` with the ASCII value of each character.
        """
        result = self.mem.poke(0, 10, "ABC")  # Página 0
        self.assertTrue(result)
        self.assertEqual(self.mem.peek(0, 10), ord("A"))
        self.assertEqual(self.mem.peek(0, 11), ord("B"))
        self.assertEqual(self.mem.peek(0, 12), ord("C"))

if __name__ == '__main__':
    unittest.main()
