"""Artifact export helpers."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def write_metrics(metrics: dict[str, float], output_dir: Path) -> Path:
    output_path = output_dir / "metrics.json"
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return output_path


def write_daily_returns(daily_returns: list[tuple[object, float]], output_dir: Path) -> Path:
    output_path = output_dir / "daily_returns.csv"
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["trade_date", "strategy_return"])
        for trade_date, value in daily_returns:
            writer.writerow([trade_date.isoformat(), round(value, 8)])
    return output_path


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


def write_report(metrics: dict[str, float | str], output_dir: Path, title: str = "QD Alpha Lab Backtest Report") -> Path:
    output_path = output_dir / "report.md"
    lines = [
        f"# {title}",
        "",
        "## Summary",
        "",
        "This report was generated from a multi-asset long-short simulation or CSV-backed price universe.",
        "The demo portfolio uses a momentum alpha with inverse-volatility scaling, while the codebase",
        "also includes mean-reversion and hybrid signal variants for research comparison.",
        "Transaction costs are charged on each rebalance.",
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
            "- Positive Sharpe indicates the alpha signal was additive after costs.",
            "- Max drawdown captures the worst peak-to-trough loss path.",
            "- Average turnover shows how aggressively the portfolio trades.",
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
            f"return {row['annualized_return']}"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path
