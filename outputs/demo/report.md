# QD Alpha Lab Demo Report

## Summary

This report was generated from a multi-asset long-short simulation or CSV-backed price universe.
The engine includes benchmark comparison, turnover-aware transaction costs, and position-level
risk controls such as gross exposure caps, turnover throttling, and volatility targeting.

## Metrics

- **strategy_name**: momentum
- **benchmark_name**: equal_weight_universe
- **annualized_return**: 0.154
- **annualized_volatility**: 0.1141
- **sharpe_ratio**: 1.3129
- **max_drawdown**: -0.0674
- **win_rate**: 0.5198
- **average_turnover**: 0.2677
- **average_gross_exposure**: 0.9779
- **benchmark_annualized_return**: 0.2947
- **benchmark_sharpe_ratio**: 1.8656
- **alpha_vs_benchmark**: -0.1407
- **beta_vs_benchmark**: 0.0336
- **correlation_vs_benchmark**: 0.0424
- **information_ratio**: -0.6615
- **days**: 227

## Interpretation

- Alpha vs benchmark shows whether the strategy outperformed a simple equal-weight universe baseline.
- Beta and correlation indicate whether the strategy is truly market-neutral in practice.
- Average turnover and gross exposure show how aggressive the risk budget is.
