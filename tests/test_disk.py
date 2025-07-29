"""_summary_
Unit tests for the Disk class in the modules.Disk module.

This test suite verifies the following functionalities:
- Writing and reading values to/from valid disk sectors.
- Handling of invalid sector indices during write and read operations.
- Handling of invalid values during write operations.

Tested methods:
- Disk.write(sector: int, value: int) -> bool
- Disk.read(sector: int) -> int

Classes:
    TestDisk: Contains unit tests for the Disk class.
"""

import unittest
from modules.Disk import Disk

class TestDisk(unittest.TestCase):
    """
    Unit tests for the Disk class.

    TestDisk contains test cases to verify the correct behavior of the Disk class, including:
    - Writing and reading valid sectors.
    - Handling invalid sector indices during write and read operations.
    - Handling invalid values during write operations.

    Test Methods:
        setUp: Initializes a Disk instance for testing.
        test_write_and_read_sector: Tests writing to and reading from a valid sector.
        test_write_invalid_sector: Tests writing to invalid sector indices.
        test_write_invalid_value: Tests writing an invalid value to a sector.
        test_read_invalid_sector: Tests reading from an invalid sector index.
    """
    def setUp(self):
        self.disk = Disk(512, "testvdisk")

    def test_write_and_read_sector(self):
        """
        Tests that writing a value to a specific disk sector and then reading from the same sector
        returns the expected value.

        This test verifies:
        - The `write` method successfully writes the value 65 to sector 10.
        - The `read` method retrieves the value 65 from sector 10, confirming data integrity.
        """
        self.assertTrue(self.disk.write(10, 65))
        self.assertEqual(self.disk.read(10), 65)

    def test_write_invalid_sector(self):
        """
        Test that writing to invalid sector indices returns False.

        This test verifies that the `write` method of the disk object correctly handles
        attempts to write to sector indices that are out of valid range (e.g., negative
        indices or indices beyond the disk's capacity) by returning False.
        """
        self.assertFalse(self.disk.write(-1, 65))
        self.assertFalse(self.disk.write(9999, 65))

    def test_write_invalid_value(self):
        """
        Test that writing an invalid value (999) to disk at position 10 returns False, indicating the operation was unsuccessful.
        """
        self.assertFalse(self.disk.write(10, 999))

    def test_read_invalid_sector(self):
        """
        Test that reading from an invalid sector (e.g., sector 9999) returns -1, indicating an error or invalid read operation.
        """
        self.assertEqual(self.disk.read(9999), -1)

if __name__ == '__main__':
    unittest.main()
