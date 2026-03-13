"""Signal generation helpers."""

from __future__ import annotations

from math import sqrt
from statistics import fmean, pstdev


def returns_from_prices(prices: list[float]) -> list[float]:
    if len(prices) < 2:
        return []
    return [(curr / prev) - 1.0 for prev, curr in zip(prices, prices[1:])]


def momentum_signal(prices: list[float], lookback: int) -> float:
    if len(prices) <= lookback:
        return 0.0
    start_price = prices[-lookback - 1]
    end_price = prices[-1]
    return (end_price / start_price) - 1.0


def mean_reversion_signal(prices: list[float], lookback: int) -> float:
    if len(prices) < lookback:
        return 0.0
    window = prices[-lookback:]
    average = fmean(window)
    dispersion = pstdev(window)
    if dispersion == 0:
        return 0.0
    z_score = (prices[-1] - average) / dispersion
    return -z_score


def volatility(prices: list[float], lookback: int) -> float:
    window_returns = returns_from_prices(prices[-(lookback + 1):])
    if len(window_returns) < 2:
        return 0.0
    return pstdev(window_returns) * sqrt(252)


def combined_signal(prices: list[float]) -> float:
    momentum = momentum_signal(prices, lookback=20)
    vol = volatility(prices, lookback=20)
    if vol == 0:
        return 0.0
    return momentum / vol
