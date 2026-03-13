"""Portfolio construction logic and strategy registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .signals import mean_reversion_signal, momentum_signal, volatility


SignalFunction = Callable[[list[float]], float]


@dataclass(frozen=True)
class StrategyConfig:
    min_history: int = 25
    gross_leverage: float = 1.0
    max_names_per_side: int = 2
    strategy_name: str = "momentum"


def momentum_vol_scaled_signal(prices: list[float]) -> float:
    vol = volatility(prices, lookback=20)
    if vol == 0:
        return 0.0
    return momentum_signal(prices, lookback=20) / vol


def mean_reversion_vol_scaled_signal(prices: list[float]) -> float:
    vol = volatility(prices, lookback=20)
    if vol == 0:
        return 0.0
    return mean_reversion_signal(prices, lookback=10) / vol


def hybrid_signal(prices: list[float]) -> float:
    vol = volatility(prices, lookback=20)
    if vol == 0:
        return 0.0
    momentum = momentum_signal(prices, lookback=20)
    reversion = mean_reversion_signal(prices, lookback=10)
    return ((0.7 * momentum) + (0.3 * reversion)) / vol


STRATEGY_REGISTRY: dict[str, SignalFunction] = {
    "momentum": momentum_vol_scaled_signal,
    "mean_reversion": mean_reversion_vol_scaled_signal,
    "hybrid": hybrid_signal,
}


def available_strategies() -> list[str]:
    return sorted(STRATEGY_REGISTRY)


def build_target_weights(
    history: dict[str, list[float]],
    config: StrategyConfig,
) -> dict[str, float]:
    signal_fn = STRATEGY_REGISTRY[config.strategy_name]
    scored = []
    for asset, prices in history.items():
        if len(prices) < config.min_history:
            continue
        scored.append((asset, signal_fn(prices)))

    if len(scored) < config.max_names_per_side * 2:
        return {asset: 0.0 for asset in history}

    scored.sort(key=lambda item: item[1])
    losers = scored[: config.max_names_per_side]
    winners = scored[-config.max_names_per_side :]

    weights = {asset: 0.0 for asset in history}
    long_weight = config.gross_leverage / 2 / len(winners)
    short_weight = -config.gross_leverage / 2 / len(losers)

    for asset, _score in winners:
        weights[asset] = long_weight
    for asset, _score in losers:
        weights[asset] = short_weight

    return weights
