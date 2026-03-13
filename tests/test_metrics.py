import unittest

from qd_alpha_lab.metrics import (
    annualized_return,
    drawdown_series,
    equity_curve,
    max_drawdown,
    rolling_sharpe_series,
    sharpe_ratio,
    win_rate,
)


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

    def test_equity_curve_grows_with_positive_returns(self) -> None:
        curve = equity_curve([0.10, 0.05])
        self.assertEqual(len(curve), 2)
        self.assertGreater(curve[-1], 1.0)

    def test_drawdown_series_tracks_declines(self) -> None:
        series = drawdown_series([0.10, -0.20, 0.05])
        self.assertEqual(round(min(series), 4), -0.2)

    def test_rolling_sharpe_series_matches_input_length(self) -> None:
        series = rolling_sharpe_series([0.01] * 25, window=5)
        self.assertEqual(len(series), 25)


if __name__ == "__main__":
    unittest.main()
