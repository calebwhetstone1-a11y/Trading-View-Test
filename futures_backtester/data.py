"""OHLCV CSV loading, timezone localization, and session filtering."""

from __future__ import annotations

import csv
from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from futures_backtester.models import BacktestSettings, Bar

REQUIRED_OHLCV_COLUMNS = {"timestamp", "open", "high", "low", "close", "volume"}


def _parse_timestamp(value: str, timezone: str) -> datetime:
    """Parse a CSV timestamp and normalize it to the configured timezone."""

    cleaned = value.strip().replace("Z", "+00:00")
    timestamp = datetime.fromisoformat(cleaned)
    tz = ZoneInfo(timezone)
    if timestamp.tzinfo is None:
        return timestamp.replace(tzinfo=tz)
    return timestamp.astimezone(tz)


def _parse_date_boundary(value: str | None, timezone: str, end: bool = False) -> datetime | None:
    """Parse optional inclusive start or exclusive end date boundaries."""

    if value is None:
        return None
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=ZoneInfo(timezone))
    else:
        parsed = parsed.astimezone(ZoneInfo(timezone))
    if end and parsed.time() == time(0, 0):
        from datetime import timedelta

        parsed = parsed + timedelta(days=1)
    return parsed


def load_ohlcv_csv(path: str | Path, settings: BacktestSettings) -> list[Bar]:
    """Load OHLCV bars from CSV and apply date/session filters using stdlib only."""

    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"OHLCV CSV not found: {csv_path}")
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_OHLCV_COLUMNS.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"OHLCV CSV missing required columns: {sorted(missing)}")
        bars = [
            Bar(
                timestamp=_parse_timestamp(row["timestamp"], settings.timezone),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )
            for row in reader
        ]
    start = _parse_date_boundary(settings.date_start, settings.timezone)
    end = _parse_date_boundary(settings.date_end, settings.timezone, end=True)
    if start is not None:
        bars = [bar for bar in bars if bar.timestamp >= start]
    if end is not None:
        bars = [bar for bar in bars if bar.timestamp < end]
    return filter_session(sorted(bars, key=lambda bar: bar.timestamp), settings)


def filter_session(bars: list[Bar], settings: BacktestSettings) -> list[Bar]:
    """Return bars whose localized timestamp falls inside the configured session."""

    tz = ZoneInfo(settings.timezone)
    filtered: list[Bar] = []
    for bar in bars:
        localized = bar.timestamp.astimezone(tz)
        if settings.session_start <= localized.time() <= settings.session_end:
            filtered.append(
                Bar(
                    timestamp=localized,
                    open=bar.open,
                    high=bar.high,
                    low=bar.low,
                    close=bar.close,
                    volume=bar.volume,
                )
            )
    return filtered
