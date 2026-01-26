import sys
import os
import unittest

# Ensure idm_logger can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from idm_logger.manufacturers import ManufacturerRegistry


class TestDriverRegistry(unittest.TestCase):
    def test_drivers_registered(self):
        mfrs = ManufacturerRegistry.list_manufacturers()

        # Check IDM
        idm = next((m for m in mfrs if m["id"] == "idm"), None)
        self.assertIsNotNone(idm)
        self.assertTrue(any(m["id"] == "navigator_2_0" for m in idm["models"]))

        # Check NIBE
        nibe = next((m for m in mfrs if m["id"] == "nibe"), None)
        self.assertIsNotNone(nibe, "NIBE manufacturer not found")
        self.assertTrue(
            any(m["id"] == "s_series" for m in nibe["models"]),
            "NIBE S-Series model not found",
        )

        # Check Daikin
        daikin = next((m for m in mfrs if m["id"] == "daikin"), None)
        self.assertIsNotNone(daikin, "Daikin manufacturer not found")
        self.assertTrue(
            any(m["id"] == "altherma" for m in daikin["models"]),
            "Daikin Altherma model not found",
        )

        # Check Luxtronik
        lux = next((m for m in mfrs if m["id"] == "luxtronik"), None)
        self.assertIsNotNone(lux, "Luxtronik manufacturer not found")
        self.assertTrue(
            any(m["id"] == "luxtronik_2_1" for m in lux["models"]),
            "Luxtronik 2.1 model not found",
        )

    def test_driver_instantiation(self):
        nibe = ManufacturerRegistry.get_driver("nibe", "s_series")
        self.assertIsNotNone(nibe)
        self.assertEqual(nibe.MANUFACTURER, "nibe")

        daikin = ManufacturerRegistry.get_driver("daikin", "altherma")
        self.assertIsNotNone(daikin)
        self.assertEqual(daikin.MANUFACTURER, "daikin")


if __name__ == "__main__":
    unittest.main()
