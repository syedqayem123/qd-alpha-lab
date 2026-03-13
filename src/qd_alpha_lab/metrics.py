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
    equity = 1.0
    peak = 1.0
    worst = 0.0
    for daily in returns:
        equity *= 1.0 + daily
        peak = max(peak, equity)
        drawdown = (equity / peak) - 1.0
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
