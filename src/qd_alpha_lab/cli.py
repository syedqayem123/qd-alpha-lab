"""Command-line entry point for the portfolio project."""

from __future__ import annotations

import argparse
from pathlib import Path

from .backtest import BacktestConfig, run_backtest
from .data import generate_market_data, load_market_data_from_csv
from .report import (
    write_daily_returns,
    write_metrics,
    write_positions,
    write_research_summary,
    write_report,
    write_sweep_results,
    write_time_series,
    write_walkforward_splits,
)
from .research import run_strategy_sweep
from .strategy import available_strategies
from .walkforward import run_walkforward


def _write_backtest_artifacts(results: dict[str, object], output_dir: Path, title: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_metrics(results["metrics"], output_dir)
    write_daily_returns(results["daily_returns"], output_dir)
    write_daily_returns(results["benchmark_returns"], output_dir, filename="benchmark_returns.csv", column_name="benchmark_return")
    write_time_series(results["equity_curve"], output_dir, filename="equity_curve.csv", value_name="equity")
    write_time_series(
        results["benchmark_equity_curve"],
        output_dir,
        filename="benchmark_equity_curve.csv",
        value_name="benchmark_equity",
    )
    write_time_series(results["drawdown_series"], output_dir, filename="drawdown_series.csv", value_name="drawdown")
    write_time_series(results["rolling_sharpe"], output_dir, filename="rolling_sharpe.csv", value_name="rolling_sharpe")
    write_positions(results["positions"], output_dir)
    write_report(results["metrics"], output_dir, title=title)


def run_demo(output_dir: Path) -> None:
    market_data = generate_market_data()
    results = run_backtest(
        market_data,
        BacktestConfig(
            transaction_cost_bps=5.0,
            gross_leverage=1.0,
            max_names_per_side=2,
            min_history=25,
            strategy_name="momentum",
        ),
    )
    _write_backtest_artifacts(results, output_dir, title="QD Alpha Lab Demo Report")
    print(f"Demo artifacts written to {output_dir}")


def run_csv_backtest(csv_path: Path, output_dir: Path, strategy_name: str) -> None:
    market_data = load_market_data_from_csv(csv_path)
    results = run_backtest(
        market_data,
        BacktestConfig(
            transaction_cost_bps=5.0,
            gross_leverage=1.0,
            max_names_per_side=2,
            min_history=25,
            strategy_name=strategy_name,
        ),
    )
    _write_backtest_artifacts(results, output_dir, title="QD Alpha Lab CSV Backtest Report")
    print(f"CSV backtest artifacts written to {output_dir}")


def run_research(csv_path: Path | None, output_dir: Path) -> None:
    market_data = load_market_data_from_csv(csv_path) if csv_path else generate_market_data()
    results = run_strategy_sweep(market_data)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_sweep_results(results, output_dir)
    write_research_summary(results, output_dir)
    print(f"Research sweep artifacts written to {output_dir}")


def run_walkforward_command(csv_path: Path | None, output_dir: Path) -> None:
    market_data = load_market_data_from_csv(csv_path) if csv_path else generate_market_data()
    results = run_walkforward(market_data)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_metrics(results["summary_metrics"], output_dir)
    write_walkforward_splits(results["splits"], output_dir)
    write_daily_returns(
        results["test_returns"],
        output_dir,
        filename="walkforward_returns.csv",
        column_name="walkforward_return",
    )
    print(f"Walk-forward artifacts written to {output_dir}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="QD Alpha Lab CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_parser = subparsers.add_parser("demo", help="Run the demo backtest")
    demo_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/demo"),
        help="Directory where artifacts should be written",
    )

    csv_parser = subparsers.add_parser("backtest-csv", help="Run a backtest on CSV price data")
    csv_parser.add_argument("csv_path", type=Path, help="CSV file in long or wide format")
    csv_parser.add_argument(
        "--strategy",
        choices=available_strategies(),
        default="momentum",
        help="Strategy to evaluate",
    )
    csv_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/csv_backtest"),
        help="Directory where artifacts should be written",
    )

    research_parser = subparsers.add_parser("research", help="Compare strategies and parameters")
    research_parser.add_argument(
        "--csv-path",
        type=Path,
        default=None,
        help="Optional CSV price file. If omitted, synthetic data is used.",
    )
    research_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/research"),
        help="Directory where research artifacts should be written",
    )

    walkforward_parser = subparsers.add_parser("walkforward", help="Run walk-forward testing")
    walkforward_parser.add_argument(
        "--csv-path",
        type=Path,
        default=None,
        help="Optional CSV price file. If omitted, synthetic data is used.",
    )
    walkforward_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/walkforward"),
        help="Directory where walk-forward artifacts should be written",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "demo":
        run_demo(args.output_dir)
    elif args.command == "backtest-csv":
        run_csv_backtest(args.csv_path, args.output_dir, args.strategy)
    elif args.command == "research":
        run_research(args.csv_path, args.output_dir)
    elif args.command == "walkforward":
        run_walkforward_command(args.csv_path, args.output_dir)


if __name__ == "__main__":
    main()
