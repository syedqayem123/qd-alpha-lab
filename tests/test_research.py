import unittest
from pathlib import Path

from qd_alpha_lab.data import load_market_data_from_csv
from qd_alpha_lab.research import run_strategy_sweep


class ResearchTestCase(unittest.TestCase):
    def test_strategy_sweep_returns_ranked_rows(self) -> None:
        market_data = load_market_data_from_csv(Path("data/sample_prices.csv"))
        rows = run_strategy_sweep(market_data, transaction_costs=[5.0], names_per_side=[1, 2])
        self.assertEqual(len(rows), 6)
        self.assertGreaterEqual(rows[0]["sharpe_ratio"], rows[-1]["sharpe_ratio"])


if __name__ == "__main__":
    unittest.main()
