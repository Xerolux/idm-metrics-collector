import unittest
from idm_logger.update_manager import _parse_version

class TestVersionParsing(unittest.TestCase):
    def test_standard_version(self):
        self.assertEqual(_parse_version("0.6.0"), (0, 6, 0))
        self.assertEqual(_parse_version("v0.6.0"), (0, 6, 0))

    def test_version_with_hash(self):
        # 0.6.abc1234 -> major=0, minor=6, patch=0 (since abc1234 is not int)
        self.assertEqual(_parse_version("0.6.abc1234"), (0, 6, 0))
        self.assertEqual(_parse_version("v0.6.abc1234"), (0, 6, 0))

    def test_version_with_numeric_hash_start(self):
        # If hash starts with numbers, they might be parsed as patch if logic isn't careful.
        # Current logic: if patch_str.isdigit() -> patch=int(patch_str), else patch=0
        # "123abcde".isdigit() is False. So patch should be 0.
        self.assertEqual(_parse_version("0.6.123abcde"), (0, 6, 0))

    def test_version_with_pure_numeric_patch(self):
        self.assertEqual(_parse_version("0.6.1"), (0, 6, 1))
        self.assertEqual(_parse_version("0.6.123"), (0, 6, 123))

    def test_short_version(self):
        self.assertEqual(_parse_version("0.6"), (0, 6, 0))

if __name__ == '__main__':
    unittest.main()
