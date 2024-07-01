import unittest


class TestClassName(unittest.TestCase):

    def test_func_name(self):
        expected = 3
        a, b = 1, 2

        actual = a + b

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
