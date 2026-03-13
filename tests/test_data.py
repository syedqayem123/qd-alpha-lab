import unittest
from pathlib import Path

from qd_alpha_lab.data import load_market_data_from_csv


class DataLoaderTestCase(unittest.TestCase):
    def test_loads_wide_csv_format(self) -> None:
        market_data = load_market_data_from_csv(Path("data/sample_prices.csv"))
        self.assertEqual(sorted(market_data), ["ALPHA", "BETA", "DELTA", "EPSILON", "GAMMA"])
        self.assertGreaterEqual(len(market_data["ALPHA"]), 30)

    def test_loaded_assets_share_same_dates(self) -> None:
        market_data = load_market_data_from_csv(Path("data/sample_prices.csv"))
        alpha_dates = [trade_date for trade_date, _close in market_data["ALPHA"]]
        beta_dates = [trade_date for trade_date, _close in market_data["BETA"]]
        self.assertEqual(alpha_dates, beta_dates)


if __name__ == "__main__":
    unittest.main()
