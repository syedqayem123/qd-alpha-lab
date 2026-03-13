"""Optional Streamlit dashboard for QD Alpha Lab artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


def _load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
    positions_path = output_dir / "positions.csv"
    sweep_path = output_dir / "strategy_sweep.csv"

    if not metrics_path.exists():
        st.warning("No metrics file found yet. Generate artifacts first with the CLI.")
        return

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    metric_cols = st.columns(4)
    metric_keys = ["annualized_return", "sharpe_ratio", "max_drawdown", "average_turnover"]
    for col, key in zip(metric_cols, metric_keys):
        col.metric(key.replace("_", " ").title(), metrics.get(key))

    if returns_path.exists():
        returns_rows = _load_csv_rows(returns_path)
        st.subheader("Daily Returns")
        st.line_chart(
            {
                "strategy_return": [float(row["strategy_return"]) for row in returns_rows],
            }
        )

    if positions_path.exists():
        st.subheader("Latest Positions")
        positions_rows = _load_csv_rows(positions_path)
        st.dataframe(positions_rows[-5:])

    if sweep_path.exists():
        st.subheader("Research Sweep")
        sweep_rows = _load_csv_rows(sweep_path)
        st.dataframe(sweep_rows)
