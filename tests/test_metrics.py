import unittest

from qd_alpha_lab.metrics import annualized_return, max_drawdown, sharpe_ratio, win_rate


class MetricsTestCase(unittest.TestCase):
    def test_win_rate(self) -> None:
        self.assertEqual(win_rate([0.01, -0.02, 0.03, 0.02]), 0.75)

    def test_max_drawdown(self) -> None:
        returns = [0.10, -0.20, 0.05]
        self.assertEqual(round(max_drawdown(returns), 4), -0.2)

    def test_sharpe_ratio_positive_for_consistent_gains(self) -> None:
        self.assertGreater(sharpe_ratio([0.01, 0.012, 0.009, 0.011]), 0)

    def test_annualized_return_zero_when_empty(self) -> None:
        self.assertEqual(annualized_return([]), 0.0)


if __name__ == "__main__":
    unittest.main()
