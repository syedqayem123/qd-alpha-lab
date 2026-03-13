import unittest
from pathlib import Path

from qd_alpha_lab.data import load_market_data_from_csv
from qd_alpha_lab.walkforward import run_walkforward


class WalkForwardTestCase(unittest.TestCase):
    def test_walkforward_produces_splits_and_summary(self) -> None:
        market_data = load_market_data_from_csv(Path("data/sample_prices.csv"))
        result = run_walkforward(market_data, train_window=40, test_window=10)
        self.assertGreaterEqual(result["summary_metrics"]["num_splits"], 1)
        self.assertEqual(len(result["splits"]), result["summary_metrics"]["num_splits"])
        self.assertIn("walkforward_sharpe_ratio", result["summary_metrics"])


if __name__ == "__main__":
    unittest.main()
