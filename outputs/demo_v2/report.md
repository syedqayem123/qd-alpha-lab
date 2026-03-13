# QD Alpha Lab Demo Report

## Summary

This report was generated from a multi-asset long-short simulation or CSV-backed price universe.
The demo portfolio uses a momentum alpha with inverse-volatility scaling, while the codebase
also includes mean-reversion and hybrid signal variants for research comparison.
Transaction costs are charged on each rebalance.

## Metrics

- **strategy_name**: momentum
- **annualized_return**: 0.1601
- **annualized_volatility**: 0.1263
- **sharpe_ratio**: 1.2392
- **max_drawdown**: -0.0975
- **win_rate**: 0.5154
- **average_turnover**: 0.3524
- **days**: 227

## Interpretation

- Positive Sharpe indicates the alpha signal was additive after costs.
- Max drawdown captures the worst peak-to-trough loss path.
- Average turnover shows how aggressively the portfolio trades.
