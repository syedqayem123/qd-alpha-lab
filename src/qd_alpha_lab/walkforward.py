"""Walk-forward evaluation helpers."""

from __future__ import annotations

from datetime import date

from .backtest import BacktestConfig, run_backtest
from .metrics import annualized_return, max_drawdown, sharpe_ratio
from .strategy import available_strategies


def _slice_market_data(
    market_data: dict[str, list[tuple[date, float]]],
    start: int,
    end: int,
) -> dict[str, list[tuple[date, float]]]:
    return {asset: rows[start:end] for asset, rows in market_data.items()}


def run_walkforward(
    market_data: dict[str, list[tuple[date, float]]],
    train_window: int = 40,
    test_window: int = 20,
) -> dict[str, object]:
    assets = sorted(market_data)
    total_periods = len(market_data[assets[0]])
    rows: list[dict[str, float | int | str]] = []
    test_returns: list[tuple[date, float]] = []

    start = 0
    split_id = 1
    while start + train_window + test_window <= total_periods:
        train_data = _slice_market_data(market_data, start, start + train_window)
        test_data = _slice_market_data(market_data, start + train_window - 25, start + train_window + test_window)

        candidates: list[tuple[float, str, int]] = []
        for strategy_name in available_strategies():
            for name_count in [1, 2]:
                result = run_backtest(
                    train_data,
                    BacktestConfig(
                        strategy_name=strategy_name,
                        max_names_per_side=name_count,
                        transaction_cost_bps=5.0,
                        min_history=25,
                    ),
                )
                candidates.append((result["metrics"]["sharpe_ratio"], strategy_name, name_count))

        candidates.sort(reverse=True)
        _score, best_strategy, best_name_count = candidates[0]

        test_result = run_backtest(
            test_data,
            BacktestConfig(
                strategy_name=best_strategy,
                max_names_per_side=best_name_count,
                transaction_cost_bps=5.0,
                min_history=25,
            ),
        )
        test_returns.extend(test_result["daily_returns"])
        rows.append(
            {
                "split_id": split_id,
                "train_start": train_data[assets[0]][0][0].isoformat(),
                "train_end": train_data[assets[0]][-1][0].isoformat(),
                "test_end": test_data[assets[0]][-1][0].isoformat(),
                "selected_strategy": best_strategy,
                "selected_names_per_side": best_name_count,
                "test_sharpe_ratio": test_result["metrics"]["sharpe_ratio"],
                "test_annualized_return": test_result["metrics"]["annualized_return"],
                "test_max_drawdown": test_result["metrics"]["max_drawdown"],
            }
        )
        split_id += 1
        start += test_window

    stitched_returns = [value for _trade_date, value in test_returns]
    return {
        "splits": rows,
        "test_returns": test_returns,
        "summary_metrics": {
            "num_splits": len(rows),
            "walkforward_days": len(test_returns),
            "walkforward_annualized_return": round(annualized_return(stitched_returns), 4) if test_returns else 0.0,
            "walkforward_sharpe_ratio": round(sharpe_ratio(stitched_returns), 4) if test_returns else 0.0,
            "walkforward_max_drawdown": round(max_drawdown(stitched_returns), 4) if test_returns else 0.0,
        },
    }
