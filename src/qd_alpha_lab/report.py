"""Artifact export helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def write_metrics(metrics: dict[str, float | int | str], output_dir: Path) -> Path:
    output_path = output_dir / "metrics.json"
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return output_path


def write_daily_returns(
    daily_returns: list[tuple[object, float]],
    output_dir: Path,
    filename: str = "daily_returns.csv",
    column_name: str = "strategy_return",
) -> Path:
    output_path = output_dir / filename
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["trade_date", column_name])
        for trade_date, value in daily_returns:
            writer.writerow([trade_date.isoformat(), round(value, 8)])
    return output_path


def write_time_series(
    rows: list[tuple[object, float]],
    output_dir: Path,
    filename: str,
    value_name: str,
) -> Path:
    return write_daily_returns(rows, output_dir, filename=filename, column_name=value_name)


def write_positions(positions: list[tuple[object, dict[str, float]]], output_dir: Path) -> Path:
    output_path = output_dir / "positions.csv"
    assets = sorted(positions[0][1]) if positions else []
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["trade_date", *assets])
        for trade_date, weights in positions:
            writer.writerow([trade_date.isoformat(), *[round(weights[asset], 6) for asset in assets]])
    return output_path


def write_sweep_results(results: list[dict[str, float | int | str]], output_dir: Path) -> Path:
    output_path = output_dir / "strategy_sweep.csv"
    if not results:
        output_path.write_text("", encoding="utf-8")
        return output_path

    fields = list(results[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    return output_path


def write_walkforward_splits(results: list[dict[str, float | int | str]], output_dir: Path) -> Path:
    output_path = output_dir / "walkforward_splits.csv"
    if not results:
        output_path.write_text("", encoding="utf-8")
        return output_path

    fields = list(results[0].keys())
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    return output_path


def write_report(metrics: dict[str, float | str], output_dir: Path, title: str = "QD Alpha Lab Backtest Report") -> Path:
    output_path = output_dir / "report.md"
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        "This report was generated from a multi-asset long-short simulation or CSV-backed price universe.",
        "The engine includes benchmark comparison, turnover-aware transaction costs, and position-level",
        "risk controls such as gross exposure caps, turnover throttling, and volatility targeting.",
        "",
        "## Metrics",
        "",
    ]
    for key, value in metrics.items():
        lines.append(f"- **{key}**: {value}")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Alpha vs benchmark shows whether the strategy outperformed a simple equal-weight universe baseline.",
            "- Beta and correlation indicate whether the strategy is truly market-neutral in practice.",
            "- Average turnover and gross exposure show how aggressive the risk budget is.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def write_research_summary(results: list[dict[str, float | int | str]], output_dir: Path) -> Path:
    output_path = output_dir / "research_summary.md"
    lines = [
        "# Strategy Research Summary",
        "",
        "## Top Configurations",
        "",
    ]
    for row in results[:5]:
        lines.append(
            f"- `{row['strategy_name']}` with {row['max_names_per_side']} names/side, "
            f"{row['transaction_cost_bps']} bps cost, Sharpe {row['sharpe_ratio']}, "
            f"alpha {row['alpha_vs_benchmark']}"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path
