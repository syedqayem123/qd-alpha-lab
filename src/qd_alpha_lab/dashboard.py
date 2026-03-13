"""Optional Streamlit dashboard for QD Alpha Lab artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _series(rows: list[dict[str, str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows]


def main() -> None:
    try:
        import streamlit as st
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Streamlit is not installed. Run `pip install streamlit` and then "
            "`streamlit run src/qd_alpha_lab/dashboard.py`."
        ) from exc

    st.set_page_config(page_title="QD Alpha Lab", layout="wide")
    st.title("QD Alpha Lab Dashboard")

    default_dir = Path("outputs/demo")
    output_dir = Path(st.text_input("Artifacts directory", str(default_dir)))

    metrics_path = output_dir / "metrics.json"
    returns_path = output_dir / "daily_returns.csv"
    benchmark_returns_path = output_dir / "benchmark_returns.csv"
    equity_path = output_dir / "equity_curve.csv"
    benchmark_equity_path = output_dir / "benchmark_equity_curve.csv"
    drawdown_path = output_dir / "drawdown_series.csv"
    rolling_sharpe_path = output_dir / "rolling_sharpe.csv"
    positions_path = output_dir / "positions.csv"
    sweep_path = output_dir / "strategy_sweep.csv"
    walkforward_path = output_dir / "walkforward_splits.csv"

    if not metrics_path.exists():
        st.warning("No metrics file found yet. Generate artifacts first with the CLI.")
        return

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metric_cols = st.columns(4)
    metric_keys = ["annualized_return", "sharpe_ratio", "alpha_vs_benchmark", "max_drawdown"]
    for col, key in zip(metric_cols, metric_keys):
        if key in metrics:
            col.metric(key.replace("_", " ").title(), metrics.get(key))

    if equity_path.exists():
        equity_rows = _load_csv_rows(equity_path)
        chart_data = {"equity": _series(equity_rows, "equity")}
        if benchmark_equity_path.exists():
            benchmark_rows = _load_csv_rows(benchmark_equity_path)
            chart_data["benchmark_equity"] = _series(benchmark_rows, "benchmark_equity")
        st.subheader("Equity Curve")
        st.line_chart(chart_data)

    if drawdown_path.exists():
        drawdown_rows = _load_csv_rows(drawdown_path)
        st.subheader("Drawdown")
        st.line_chart({"drawdown": _series(drawdown_rows, "drawdown")})

    if rolling_sharpe_path.exists():
        rolling_rows = _load_csv_rows(rolling_sharpe_path)
        st.subheader("Rolling Sharpe")
        st.line_chart({"rolling_sharpe": _series(rolling_rows, "rolling_sharpe")})

    if returns_path.exists():
        returns_rows = _load_csv_rows(returns_path)
        chart_data = {"strategy_return": _series(returns_rows, "strategy_return")}
        if benchmark_returns_path.exists():
            benchmark_rows = _load_csv_rows(benchmark_returns_path)
            chart_data["benchmark_return"] = _series(benchmark_rows, "benchmark_return")
        st.subheader("Daily Returns")
        st.line_chart(chart_data)

    if positions_path.exists():
        st.subheader("Latest Positions")
        positions_rows = _load_csv_rows(positions_path)
        st.dataframe(positions_rows[-5:])

    if sweep_path.exists():
        st.subheader("Research Sweep")
        st.dataframe(_load_csv_rows(sweep_path))

    if walkforward_path.exists():
        st.subheader("Walk-Forward Splits")
        st.dataframe(_load_csv_rows(walkforward_path))
