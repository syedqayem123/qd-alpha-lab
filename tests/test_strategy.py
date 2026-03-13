import unittest

from qd_alpha_lab.strategy import StrategyConfig, available_strategies, build_target_weights


class StrategyTestCase(unittest.TestCase):
    def test_strategy_returns_flat_weights_without_history(self) -> None:
        history = {
            "A": [100.0, 101.0],
            "B": [100.0, 99.0],
            "C": [100.0, 101.5],
            "D": [100.0, 98.5],
        }
        weights = build_target_weights(history, StrategyConfig(min_history=5, max_names_per_side=1))
        self.assertTrue(all(weight == 0.0 for weight in weights.values()))

    def test_strategy_is_market_neutral_when_ready(self) -> None:
        history = {
            "A": [100.0 + i * 0.8 for i in range(30)],
            "B": [100.0 + i * 0.7 for i in range(30)],
            "C": [120.0 - i * 0.6 for i in range(30)],
            "D": [110.0 - i * 0.5 for i in range(30)],
        }
        weights = build_target_weights(history, StrategyConfig(min_history=25, max_names_per_side=1))
        self.assertEqual(round(sum(weights.values()), 8), 0.0)
        self.assertEqual(sorted(set(weights.values())), [-0.5, 0.0, 0.5])

    def test_strategy_registry_exposes_expected_variants(self) -> None:
        self.assertEqual(available_strategies(), ["hybrid", "mean_reversion", "momentum"])


if __name__ == "__main__":
    unittest.main()
