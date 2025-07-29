import unittest
from modules.CpuX8086 import RegisterSet

class TestRegisterSet(unittest.TestCase):
    def setUp(self):
        self.regs = RegisterSet()

    def test_get_and_set_register(self):
        self.regs.set("AX", 0x1234)
        self.assertEqual(self.regs.get("AX"), 0x1234)

    def test_update_flags(self):
        self.regs.update_flags(0)
        self.assertEqual(self.regs.flags["ZF"], 1)
        self.assertEqual(self.regs.flags["SF"], 0)
        self.assertEqual(self.regs.flags["PF"], 1)

    def test_set_upper_and_lower(self):
        self.assertEqual(self.regs.set_register_upper(0x00FF, 0x12), 0x12FF)
        self.assertEqual(self.regs.set_register_lower(0xFF00, 0x34), 0xFF34)

if __name__ == '__main__':
    unittest.main()