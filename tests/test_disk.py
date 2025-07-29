import unittest
from modules.Disk import Disk

class TestDisk(unittest.TestCase):
    def setUp(self):
        self.disk = Disk(512, "testvdisk")

    def test_write_and_read_sector(self):
        self.assertTrue(self.disk.write(10, 65))
        self.assertEqual(self.disk.read(10), 65)

    def test_write_invalid_sector(self):
        self.assertFalse(self.disk.write(-1, 65))
        self.assertFalse(self.disk.write(9999, 65))

    def test_write_invalid_value(self):
        self.assertFalse(self.disk.write(10, 999))

    def test_read_invalid_sector(self):
        self.assertEqual(self.disk.read(9999), -1)

if __name__ == '__main__':
    unittest.main()
