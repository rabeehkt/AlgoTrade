import unittest

from main import normalize_tradingsymbol


class TestMainHelpers(unittest.TestCase):
    def test_normalize_tradingsymbol_with_exchange_prefix(self):
        self.assertEqual(normalize_tradingsymbol("NSE:INFY"), "INFY")

    def test_normalize_tradingsymbol_without_exchange_prefix(self):
        self.assertEqual(normalize_tradingsymbol("TCS"), "TCS")


if __name__ == "__main__":
    unittest.main()
