"""Synthetic and CSV-based market data loading."""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta
from pathlib import Path
from random import Random


def _business_days(start: date, periods: int) -> list[date]:
    days: list[date] = []
    current = start
    while len(days) < periods:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def generate_market_data(
    num_assets: int = 8,
    periods: int = 252,
    seed: int = 7,
    start: date = date(2024, 1, 1),
) -> dict[str, list[tuple[date, float]]]:
    """Generate deterministic multi-asset close prices."""

    rng = Random(seed)
    dates = _business_days(start, periods)
    market_series = []
    level = 0.0
    for idx in range(periods):
        cycle = 0.0007 if idx % 40 < 20 else -0.0004
        shock = rng.gauss(0.0003, 0.0075)
        level += cycle + shock
        market_series.append(level)

    prices: dict[str, list[tuple[date, float]]] = {}
    for asset_idx in range(num_assets):
        asset = f"ASSET_{asset_idx + 1}"
        price = 90.0 + asset_idx * 7.5
        beta = 0.8 + (asset_idx % 4) * 0.15
        asset_path: list[tuple[date, float]] = []
        for idx, trade_date in enumerate(dates):
            idio = rng.gauss(0.0, 0.012 + asset_idx * 0.0008)
            reversal = -0.0025 if idx % 17 == asset_idx % 5 else 0.0
            trend_boost = 0.0015 if (idx + asset_idx) % 55 < 12 else 0.0
            daily_return = beta * (market_series[idx] - (market_series[idx - 1] if idx else 0.0))
            daily_return += idio + reversal + trend_boost
            price *= max(0.90, 1.0 + daily_return)
            asset_path.append((trade_date, round(price, 4)))
        prices[asset] = asset_path

    return prices


def _parse_date(value: str) -> date:
    return datetime.strptime(value.strip(), "%Y-%m-%d").date()


def _normalize_market_data(raw: dict[str, list[tuple[date, float]]]) -> dict[str, list[tuple[date, float]]]:
    normalized = {asset: sorted(rows, key=lambda item: item[0]) for asset, rows in raw.items() if rows}
    if not normalized:
        raise ValueError("No rows were loaded from the CSV file.")

    shared_dates = None
    for rows in normalized.values():
        asset_dates = {trade_date for trade_date, _close in rows}
        shared_dates = asset_dates if shared_dates is None else shared_dates & asset_dates

    if not shared_dates:
        raise ValueError("Assets do not share enough overlapping dates for backtesting.")

    aligned_dates = sorted(shared_dates)
    aligned: dict[str, list[tuple[date, float]]] = {}
    for asset, rows in normalized.items():
        lookup = {trade_date: close for trade_date, close in rows}
        aligned[asset] = [(trade_date, lookup[trade_date]) for trade_date in aligned_dates]
    return aligned


def load_market_data_from_csv(csv_path: Path) -> dict[str, list[tuple[date, float]]]:
    """Load market data from either long or wide CSV format.

    Supported schemas:
    - long: trade_date, asset, close
    - wide: trade_date, ASSET_A, ASSET_B, ...
    """

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        if {"trade_date", "asset", "close"}.issubset(fieldnames):
            raw: dict[str, list[tuple[date, float]]] = {}
            for row in reader:
                asset = row["asset"].strip()
                raw.setdefault(asset, []).append((_parse_date(row["trade_date"]), float(row["close"])))
            return _normalize_market_data(raw)

        if fieldnames and fieldnames[0] == "trade_date" and len(fieldnames) > 1:
            raw = {asset: [] for asset in fieldnames[1:]}
            for row in reader:
                trade_date = _parse_date(row["trade_date"])
                for asset in fieldnames[1:]:
                    value = row.get(asset, "").strip()
                    if value:
                        raw[asset].append((trade_date, float(value)))
            return _normalize_market_data(raw)

    raise ValueError(
        "Unsupported CSV schema. Use either columns trade_date,asset,close or trade_date plus one column per asset."
    )
