# Xerolux 2026
# SPDX-License-Identifier: MIT
import unittest
from idm_logger.update_manager import _parse_version


class TestVersionParsing(unittest.TestCase):
    def test_standard_version(self):
        # (major, minor, patch, type, prerelease_num)
        # Type 1 = stable
        self.assertEqual(_parse_version("0.6.0"), (0, 6, 0, 1, 0))
        self.assertEqual(_parse_version("v0.6.0"), (0, 6, 0, 1, 0))

    def test_version_with_hash(self):
        # Type 2 = dev/hash
        self.assertEqual(_parse_version("0.6.abc1234"), (0, 6, 0, 2, 0))
        self.assertEqual(_parse_version("v0.6.abc1234"), (0, 6, 0, 2, 0))

    def test_version_with_numeric_hash_start(self):
        # "123abcde".isdigit() is False.
        self.assertEqual(_parse_version("0.6.123abcde"), (0, 6, 0, 2, 0))

    def test_version_with_pure_numeric_patch(self):
        self.assertEqual(_parse_version("0.6.1"), (0, 6, 1, 1, 0))
        self.assertEqual(_parse_version("0.6.123"), (0, 6, 123, 1, 0))

    def test_short_version(self):
        self.assertEqual(_parse_version("0.6"), (0, 6, 0, 1, 0))

    def test_beta_version(self):
        # Type 0 = beta/prerelease
        self.assertEqual(_parse_version("0.6.0-beta1"), (0, 6, 0, 0, 1))
        self.assertEqual(_parse_version("v0.6.0-beta2"), (0, 6, 0, 0, 2))

    def test_alpha_version(self):
        # We treat alpha same as beta in parsing logic currently (just prerelease)
        # alpha1 -> 1
        self.assertEqual(_parse_version("0.6.0-alpha1"), (0, 6, 0, 0, 1))

    def test_comparison(self):
        # Verify comparison logic works as expected
        v_stable = _parse_version("0.6.0")
        v_beta = _parse_version("0.6.0-beta1")
        v_old = _parse_version("0.5.9")

        # (0,6,0,1,0) > (0,6,0,0,1) -> Stable > Beta
        self.assertTrue(v_stable > v_beta)

        # (0,6,0,0,1) > (0,5,9,1,0) -> Beta 0.6.0 > Stable 0.5.9
        self.assertTrue(v_beta > v_old)

        v_beta2 = _parse_version("0.6.0-beta2")
        self.assertTrue(v_beta2 > v_beta)


if __name__ == "__main__":
    unittest.main()
