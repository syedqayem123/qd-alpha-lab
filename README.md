# QD Alpha Lab

`QD Alpha Lab` is a resume-ready quantitative developer project that now covers three portfolio-grade workflows:

- synthetic multi-asset market simulation for reproducible demos
- real CSV ingestion for NSE or US equity-style daily close data
- research sweeps across multiple alpha strategies and transaction-cost assumptions
- optional Streamlit dashboard for presenting results visually

## Why this is a strong shortlist project

This project demonstrates the mix recruiters usually want from a fresher quant developer:

- clean Python package structure
- separation of data, signals, portfolio construction, research, and reporting
- realistic assumptions such as transaction costs and turnover tracking
- multiple strategy variants instead of a single hard-coded idea
- test coverage on quant logic and data loading
- recruiter-friendly outputs in CSV, JSON, and Markdown

## Project Structure

```text
.
├── data
│   └── sample_prices.csv
├── outputs
├── pyproject.toml
├── README.md
├── src/qd_alpha_lab
│   ├── __init__.py
│   ├── backtest.py
│   ├── cli.py
│   ├── dashboard.py
│   ├── data.py
│   ├── metrics.py
│   ├── report.py
│   ├── research.py
│   ├── signals.py
│   └── strategy.py
└── tests
    ├── test_data.py
    ├── test_metrics.py
    ├── test_research.py
    └── test_strategy.py
```

## Included Strategies

The backtester supports three ranking-based market-neutral strategies:

- `momentum`: medium-term trend signal scaled by inverse volatility
- `mean_reversion`: short-term z-score reversal signal scaled by inverse volatility
- `hybrid`: weighted blend of momentum and mean reversion

Each day, the engine ranks assets cross-sectionally, goes long the strongest names, shorts the weakest names, and charges transaction costs based on turnover.

## 1. Run the Demo

```bash
PYTHONPATH=src python3 -m qd_alpha_lab.cli demo --output-dir outputs/demo
```

This generates:

- `metrics.json`
- `daily_returns.csv`
- `positions.csv`
- `report.md`

## 2. Run a Backtest on Real CSV Data

A sample price file is bundled at [data/sample_prices.csv](/Users/s0m0zg3/personal/trading/data/sample_prices.csv).

```bash
PYTHONPATH=src python3 -m qd_alpha_lab.cli backtest-csv data/sample_prices.csv --strategy momentum --output-dir outputs/csv_backtest
```

Supported CSV schemas:

- long format: `trade_date,asset,close`
- wide format: `trade_date,ASSET_A,ASSET_B,...`

## 3. Run Multi-Strategy Research Sweeps

```bash
PYTHONPATH=src python3 -m qd_alpha_lab.cli research --csv-path data/sample_prices.csv --output-dir outputs/research
```

This compares strategies, names-per-side, and cost assumptions, then writes:

- `strategy_sweep.csv`
- `research_summary.md`

## 4. Launch the Dashboard

The dashboard is optional so the core project stays lightweight.

```bash
pip install ".[dashboard]"
streamlit run src/qd_alpha_lab/dashboard.py
```

Point the app at `outputs/demo`, `outputs/csv_backtest`, or `outputs/research` to inspect the generated artifacts.

## Run Tests

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Suggested Resume Bullets

- Built a Python-based quantitative research platform for market-neutral long-short strategies, including CSV data ingestion, signal generation, portfolio construction, transaction cost modeling, and performance reporting.
- Implemented momentum, mean-reversion, and hybrid alpha models with volatility scaling, and compared them through parameter sweeps using Sharpe ratio, CAGR, drawdown, turnover, and hit-rate analytics.
- Developed a reproducible CLI and Streamlit workflow that generates backtest artifacts and research summaries from both synthetic and real price data.

## How to talk about it in interviews

- explain why cross-sectional ranking is common in stat-arb and equities strategies
- discuss how transaction costs and turnover can destroy naive alpha
- mention why you built both reproducible simulation and real CSV ingestion
- describe how the research sweep helps choose a strategy instead of curve-fitting one setup
- point out that the dashboard is for communicating results to PMs, researchers, or interviewers

## Good next upgrades

- add sector or beta neutrality constraints
- support intraday bars and delayed fills
- add benchmark comparison and factor attribution
- ingest broker or exchange-format data directly
