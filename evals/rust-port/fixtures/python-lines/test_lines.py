import unittest
from lines import split_nonempty


class LineTests(unittest.TestCase):
    def test_python_separators(self):
        for separator in ('\n', '\r', '\r\n', '\v', '\f', '\x1c', '\x1d', '\x1e', '\x85', '\u2028', '\u2029'):
            self.assertEqual(split_nonempty('a'+separator+'b'+separator), ['a', 'b'])

    def test_whitespace_is_not_trimmed(self):
        self.assertEqual(split_nonempty(' a \n \nb '), [' a ', ' ', 'b '])

    def test_empty_lines_are_removed(self):
        self.assertEqual(split_nonempty('\n\r\n'), [])
        self.assertEqual(split_nonempty(''), [])

    def test_other_control_characters_are_content(self):
        self.assertEqual(split_nonempty('a\x1fb'), ['a\x1fb'])


if __name__ == '__main__':
    unittest.main()
