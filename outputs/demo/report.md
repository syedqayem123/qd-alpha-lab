# QD Alpha Lab Backtest Report

## Summary

This report was generated from a deterministic multi-asset long-short simulation.
The demo portfolio uses a momentum alpha with inverse-volatility scaling, while the codebase
also includes a mean-reversion prototype for signal research and extension.
Transaction costs are charged on each rebalance.

## Metrics

- **annualized_return**: 0.1437
- **annualized_volatility**: 0.1201
- **sharpe_ratio**: 1.1782
- **max_drawdown**: -0.0975
- **win_rate**: 0.4661
- **average_turnover**: 0.3187
- **days**: 251

## Interpretation

- Positive Sharpe indicates the alpha signal was additive after costs.
- Max drawdown captures the worst peak-to-trough loss path.
- Average turnover shows how aggressively the portfolio trades.
