"""Performance and risk metrics."""

from __future__ import annotations

from math import prod, sqrt
from statistics import fmean, pstdev


def annualized_return(returns: list[float], periods_per_year: int = 252) -> float:
    if not returns:
        return 0.0
    total_return = prod(1.0 + daily for daily in returns)
    years = len(returns) / periods_per_year
    if years == 0:
        return 0.0
    return total_return ** (1 / years) - 1.0


def annualized_volatility(returns: list[float], periods_per_year: int = 252) -> float:
    if len(returns) < 2:
        return 0.0
    return pstdev(returns) * sqrt(periods_per_year)


def sharpe_ratio(returns: list[float], risk_free_rate: float = 0.0) -> float:
    if len(returns) < 2:
        return 0.0
    rf_daily = risk_free_rate / 252
    excess = [daily - rf_daily for daily in returns]
    sigma = pstdev(excess)
    if sigma == 0:
        return 0.0
    return fmean(excess) / sigma * sqrt(252)


def max_drawdown(returns: list[float]) -> float:
    worst = 0.0
    for drawdown in drawdown_series(returns):
        worst = min(worst, drawdown)
    return worst


def win_rate(returns: list[float]) -> float:
    if not returns:
        return 0.0
    wins = sum(1 for daily in returns if daily > 0)
    return wins / len(returns)


def average_turnover(turnovers: list[float]) -> float:
    if not turnovers:
        return 0.0
    return fmean(turnovers)


def equity_curve(returns: list[float], start_value: float = 1.0) -> list[float]:
    equity = start_value
    curve: list[float] = []
    for daily in returns:
        equity *= 1.0 + daily
        curve.append(equity)
    return curve


def drawdown_series(returns: list[float]) -> list[float]:
    curve = equity_curve(returns)
    peak = 1.0
    series: list[float] = []
    for equity in curve:
        peak = max(peak, equity)
        series.append((equity / peak) - 1.0)
    return series


def rolling_sharpe_series(returns: list[float], window: int = 20) -> list[float]:
    if window <= 1:
        raise ValueError("Rolling window must be greater than 1.")
    series: list[float] = []
    for idx in range(len(returns)):
        if idx + 1 < window:
            series.append(0.0)
            continue
        series.append(sharpe_ratio(returns[idx + 1 - window : idx + 1]))
    return series


def correlation(left: list[float], right: list[float]) -> float:
    if len(left) != len(right) or len(left) < 2:
        return 0.0
    left_mean = fmean(left)
    right_mean = fmean(right)
    left_std = pstdev(left)
    right_std = pstdev(right)
    if left_std == 0 or right_std == 0:
        return 0.0
    cov = sum((l - left_mean) * (r - right_mean) for l, r in zip(left, right)) / len(left)
    return cov / (left_std * right_std)


def beta(strategy_returns: list[float], benchmark_returns: list[float]) -> float:
    if len(strategy_returns) != len(benchmark_returns) or len(strategy_returns) < 2:
        return 0.0
    benchmark_mean = fmean(benchmark_returns)
    variance = sum((value - benchmark_mean) ** 2 for value in benchmark_returns) / len(benchmark_returns)
    if variance == 0:
        return 0.0
    strategy_mean = fmean(strategy_returns)
    cov = (
        sum(
            (strategy_value - strategy_mean) * (benchmark_value - benchmark_mean)
            for strategy_value, benchmark_value in zip(strategy_returns, benchmark_returns)
        )
        / len(strategy_returns)
    )
    return cov / variance


def information_ratio(strategy_returns: list[float], benchmark_returns: list[float]) -> float:
    if len(strategy_returns) != len(benchmark_returns) or len(strategy_returns) < 2:
        return 0.0
    active_returns = [strategy - benchmark for strategy, benchmark in zip(strategy_returns, benchmark_returns)]
    sigma = pstdev(active_returns)
    if sigma == 0:
        return 0.0
    return fmean(active_returns) / sigma * sqrt(252)
