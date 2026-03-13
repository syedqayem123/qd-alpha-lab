"""Simple daily portfolio backtest engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from .metrics import (
    annualized_return,
    annualized_volatility,
    average_turnover,
    max_drawdown,
    sharpe_ratio,
    win_rate,
)
from .signals import returns_from_prices
from .strategy import StrategyConfig, build_target_weights


@dataclass(frozen=True)
class BacktestConfig:
    transaction_cost_bps: float = 10.0
    gross_leverage: float = 1.0
    max_names_per_side: int = 2
    min_history: int = 25
    strategy_name: str = "momentum"


def run_backtest(
    market_data: dict[str, list[tuple[date, float]]],
    config: BacktestConfig | None = None,
) -> dict[str, Any]:
    config = config or BacktestConfig()
    assets = sorted(market_data)
    dates = [trade_date for trade_date, _price in market_data[assets[0]]]
    price_history = {asset: [price for _trade_date, price in market_data[asset]] for asset in assets}
    strategy_config = StrategyConfig(
        min_history=config.min_history,
        gross_leverage=config.gross_leverage,
        max_names_per_side=config.max_names_per_side,
        strategy_name=config.strategy_name,
    )

    previous_weights = {asset: 0.0 for asset in assets}
    daily_returns: list[tuple[date, float]] = []
    positions: list[tuple[date, dict[str, float]]] = []
    turnovers: list[float] = []

    start_idx = max(config.min_history - 1, 0)
    for idx in range(start_idx, len(dates) - 1):
        history = {asset: price_history[asset][: idx + 1] for asset in assets}
        target_weights = build_target_weights(history, strategy_config)
        next_day_asset_returns = {
            asset: returns_from_prices(price_history[asset][idx : idx + 2])[0] for asset in assets
        }

        turnover = sum(abs(target_weights[asset] - previous_weights[asset]) for asset in assets)
        cost = turnover * (config.transaction_cost_bps / 10_000)
        gross_return = sum(target_weights[asset] * next_day_asset_returns[asset] for asset in assets)
        net_return = gross_return - cost

        trade_date = dates[idx + 1]
        daily_returns.append((trade_date, net_return))
        positions.append((trade_date, target_weights))
        turnovers.append(turnover)
        previous_weights = target_weights

    return_series = [value for _trade_date, value in daily_returns]
    metrics = {
        "strategy_name": config.strategy_name,
        "annualized_return": round(annualized_return(return_series), 4),
        "annualized_volatility": round(annualized_volatility(return_series), 4),
        "sharpe_ratio": round(sharpe_ratio(return_series), 4),
        "max_drawdown": round(max_drawdown(return_series), 4),
        "win_rate": round(win_rate(return_series), 4),
        "average_turnover": round(average_turnover(turnovers), 4),
        "days": len(return_series),
    }

    return {
        "metrics": metrics,
        "daily_returns": daily_returns,
        "positions": positions,
        "turnovers": turnovers,
    }
