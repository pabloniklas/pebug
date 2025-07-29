import unittest
from modules.Memory import Memory

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.mem = Memory()  # Crea una sola página: página 0

    def test_poke_and_peek_int(self):
        result = self.mem.poke(0, 100, 123)  # Página 0, válida
        self.assertTrue(result)
        self.assertEqual(self.mem.peek(0, 100), 123)

    def test_poke_invalid_value(self):
        self.assertFalse(self.mem.poke(0, 65536, 255))  # Dirección inválida
        self.assertFalse(self.mem.poke(0, 0, 999))      # Valor inválido

    def test_poke_string(self):
        result = self.mem.poke(0, 10, "ABC")  # Página 0
        self.assertTrue(result)
        self.assertEqual(self.mem.peek(0, 10), ord("A"))
        self.assertEqual(self.mem.peek(0, 11), ord("B"))
        self.assertEqual(self.mem.peek(0, 12), ord("C"))

if __name__ == '__main__':
    unittest.main()
