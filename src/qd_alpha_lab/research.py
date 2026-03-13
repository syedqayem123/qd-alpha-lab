"""Research helpers for comparing strategies and parameters."""

from __future__ import annotations

from datetime import date

from .backtest import BacktestConfig, run_backtest
from .strategy import available_strategies


def run_strategy_sweep(
    market_data: dict[str, list[tuple[date, float]]],
    transaction_costs: list[float] | None = None,
    names_per_side: list[int] | None = None,
) -> list[dict[str, float | int | str]]:
    transaction_costs = transaction_costs or [2.0, 5.0, 10.0]
    names_per_side = names_per_side or [1, 2, 3]
    rows: list[dict[str, float | int | str]] = []
    max_feasible_names = max(1, len(market_data) // 2)

    for strategy_name in available_strategies():
        for cost in transaction_costs:
            for name_count in names_per_side:
                if name_count > max_feasible_names:
                    continue
                result = run_backtest(
                    market_data,
                    BacktestConfig(
                        transaction_cost_bps=cost,
                        gross_leverage=1.0,
                        max_names_per_side=name_count,
                        min_history=25,
                        strategy_name=strategy_name,
                    ),
                )
                row = {
                    "strategy_name": strategy_name,
                    "transaction_cost_bps": cost,
                    "max_names_per_side": name_count,
                }
                row.update(result["metrics"])
                rows.append(row)

    rows.sort(key=lambda row: (row["sharpe_ratio"], row["annualized_return"]), reverse=True)
    return rows
