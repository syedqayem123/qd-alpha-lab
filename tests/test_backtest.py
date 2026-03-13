import unittest
from pathlib import Path

from qd_alpha_lab.backtest import BacktestConfig, run_backtest
from qd_alpha_lab.data import load_market_data_from_csv


class BacktestTestCase(unittest.TestCase):
    def test_backtest_exposes_benchmark_and_risk_metrics(self) -> None:
        market_data = load_market_data_from_csv(Path("data/sample_prices.csv"))
        result = run_backtest(
            market_data,
            BacktestConfig(
                strategy_name="momentum",
                max_names_per_side=2,
                transaction_cost_bps=5.0,
                min_history=25,
            ),
        )
        metrics = result["metrics"]
        self.assertIn("alpha_vs_benchmark", metrics)
        self.assertIn("beta_vs_benchmark", metrics)
        self.assertIn("average_gross_exposure", metrics)
        self.assertEqual(len(result["daily_returns"]), len(result["benchmark_returns"]))
        self.assertEqual(len(result["daily_returns"]), len(result["equity_curve"]))


if __name__ == "__main__":
    unittest.main()
