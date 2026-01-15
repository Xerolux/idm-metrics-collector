import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import collections
import random

# Mock the imports that might fail or are not needed for this isolated test
import sys
sys.modules['idm_logger.config'] = MagicMock()
sys.modules['idm_logger.config'].DATA_DIR = '.'

from idm_logger.ai.models import RollingWindowStats, IsolationForestModel

class TestAIModels(unittest.TestCase):

    def test_rolling_window(self):
        print("\nTesting Rolling Window Stats...")
        model = RollingWindowStats(window_size=50)

        # Train with "noisy" normal data (mean=10)
        # Adding slight noise ensures std != 0
        for _ in range(30):
            val = 10.0 + random.uniform(-0.1, 0.1)
            model.update({"temp": val})

        # Detect normal
        res = model.detect({"temp": 10.0}, sensitivity=3.0)
        self.assertEqual(len(res), 0)

        # Detect anomaly (huge spike)
        # With mean ~10 and std ~0.05, 100 is > 1000 sigma
        res = model.detect({"temp": 100.0}, sensitivity=3.0)
        print(f"Rolling Anomaly result: {res}")
        self.assertIn("temp", res)
        self.assertEqual(res["temp"]["model"], "RollingWindow")

    def test_isolation_forest(self):
        print("\nTesting Isolation Forest...")
        try:
            from sklearn.ensemble import IsolationForest
        except ImportError:
            print("Skipping Isolation Forest test (sklearn not installed)")
            return

        model = IsolationForestModel(buffer_size=200)

        # Train with normal data
        for _ in range(100):
            model.update({"temp": 10.0 + np.random.normal(0, 0.1)})

        # Should detect extreme outlier
        res = model.detect({"temp": 1000.0}, sensitivity=3.0)
        print(f"IF Anomaly result: {res}")
        self.assertIn("temp", res)
        self.assertEqual(res["temp"]["model"], "IsolationForest")

if __name__ == '__main__':
    unittest.main()
