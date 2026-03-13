"""Simple daily portfolio backtest engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from .metrics import (
    annualized_return,
    annualized_volatility,
    average_turnover,
    beta,
    correlation,
    drawdown_series,
    equity_curve,
    information_ratio,
    max_drawdown,
    rolling_sharpe_series,
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
    max_position_weight: float = 0.35
    turnover_limit: float = 0.4
    target_annual_volatility: float = 0.12
    benchmark_name: str = "equal_weight_universe"


def _scale_weights(weights: dict[str, float], gross_target: float, max_position_weight: float) -> dict[str, float]:
    capped = {
        asset: max(-max_position_weight, min(max_position_weight, weight))
        for asset, weight in weights.items()
    }
    gross = sum(abs(weight) for weight in capped.values())
    if gross == 0:
        return capped
    scale = min(1.0, gross_target / gross)
    return {asset: weight * scale for asset, weight in capped.items()}


def _apply_turnover_limit(
    previous: dict[str, float],
    target: dict[str, float],
    turnover_limit: float,
) -> tuple[dict[str, float], float]:
    raw_turnover = sum(abs(target[asset] - previous[asset]) for asset in target)
    if raw_turnover == 0 or raw_turnover <= turnover_limit:
        return target, raw_turnover

    scale = turnover_limit / raw_turnover
    adjusted = {
        asset: previous[asset] + (target[asset] - previous[asset]) * scale
        for asset in target
    }
    return adjusted, turnover_limit


def _benchmark_return(asset_returns: dict[str, float]) -> float:
    if not asset_returns:
        return 0.0
    return sum(asset_returns.values()) / len(asset_returns)


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
    benchmark_returns: list[tuple[date, float]] = []
    positions: list[tuple[date, dict[str, float]]] = []
    turnovers: list[float] = []
    realized_gross_exposure: list[float] = []
    gross_return_history: list[float] = []

    start_idx = max(config.min_history - 1, 0)
    for idx in range(start_idx, len(dates) - 1):
        history = {asset: price_history[asset][: idx + 1] for asset in assets}
        target_weights = build_target_weights(history, strategy_config)
        target_weights = _scale_weights(
            target_weights,
            gross_target=config.gross_leverage,
            max_position_weight=config.max_position_weight,
        )
        target_weights, turnover = _apply_turnover_limit(
            previous_weights,
            target_weights,
            turnover_limit=config.turnover_limit,
        )

        next_day_asset_returns = {
            asset: returns_from_prices(price_history[asset][idx : idx + 2])[0] for asset in assets
        }
        benchmark_daily_return = _benchmark_return(next_day_asset_returns)
        benchmark_returns.append((dates[idx + 1], benchmark_daily_return))

        cost = turnover * (config.transaction_cost_bps / 10_000)
        gross_return = sum(target_weights[asset] * next_day_asset_returns[asset] for asset in assets)
        gross_return_history.append(gross_return)

        if len(gross_return_history) >= 20:
            realized_vol = annualized_volatility(gross_return_history[-20:])
            vol_scale = min(1.5, config.target_annual_volatility / realized_vol) if realized_vol > 0 else 1.0
        else:
            vol_scale = 1.0

        scaled_weights = {asset: weight * vol_scale for asset, weight in target_weights.items()}
        scaled_weights = _scale_weights(
            scaled_weights,
            gross_target=config.gross_leverage,
            max_position_weight=config.max_position_weight,
        )
        gross_return = sum(scaled_weights[asset] * next_day_asset_returns[asset] for asset in assets)
        net_return = gross_return - cost

        trade_date = dates[idx + 1]
        daily_returns.append((trade_date, net_return))
        positions.append((trade_date, scaled_weights))
        turnovers.append(turnover)
        realized_gross_exposure.append(sum(abs(weight) for weight in scaled_weights.values()))
        previous_weights = scaled_weights

    return_series = [value for _trade_date, value in daily_returns]
    benchmark_series = [value for _trade_date, value in benchmark_returns]
    metrics = {
        "strategy_name": config.strategy_name,
        "benchmark_name": config.benchmark_name,
        "annualized_return": round(annualized_return(return_series), 4),
        "annualized_volatility": round(annualized_volatility(return_series), 4),
        "sharpe_ratio": round(sharpe_ratio(return_series), 4),
        "max_drawdown": round(max_drawdown(return_series), 4),
        "win_rate": round(win_rate(return_series), 4),
        "average_turnover": round(average_turnover(turnovers), 4),
        "average_gross_exposure": round(average_turnover(realized_gross_exposure), 4),
        "benchmark_annualized_return": round(annualized_return(benchmark_series), 4),
        "benchmark_sharpe_ratio": round(sharpe_ratio(benchmark_series), 4),
        "alpha_vs_benchmark": round(annualized_return(return_series) - annualized_return(benchmark_series), 4),
        "beta_vs_benchmark": round(beta(return_series, benchmark_series), 4),
        "correlation_vs_benchmark": round(correlation(return_series, benchmark_series), 4),
        "information_ratio": round(information_ratio(return_series, benchmark_series), 4),
        "days": len(return_series),
    }

    return {
        "metrics": metrics,
        "daily_returns": daily_returns,
        "benchmark_returns": benchmark_returns,
        "equity_curve": list(zip([trade_date for trade_date, _ in daily_returns], equity_curve(return_series))),
        "benchmark_equity_curve": list(
            zip([trade_date for trade_date, _ in benchmark_returns], equity_curve(benchmark_series))
        ),
        "drawdown_series": list(zip([trade_date for trade_date, _ in daily_returns], drawdown_series(return_series))),
        "rolling_sharpe": list(
            zip([trade_date for trade_date, _ in daily_returns], rolling_sharpe_series(return_series, window=20))
        ),
        "positions": positions,
        "turnovers": turnovers,
    }
