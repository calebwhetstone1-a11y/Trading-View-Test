"""Dependency-free indicator calculations used by strategies."""

from __future__ import annotations

from futures_backtester.models import Bar


def ema(values: list[float], period: int) -> list[float | None]:
    """Exponential moving average calculated incrementally without look-ahead."""

    if period <= 0:
        raise ValueError("period must be positive")
    if not values:
        return []
    alpha = 2 / (period + 1)
    result: list[float | None] = []
    current: float | None = None
    for value in values:
        current = value if current is None else alpha * value + (1 - alpha) * current
        result.append(current)
    return result


def atr(bars: list[Bar], period: int) -> list[float | None]:
    """Average true range using current and previous bar only."""

    if period <= 0:
        raise ValueError("period must be positive")
    ranges: list[float] = []
    output: list[float | None] = []
    previous_close: float | None = None
    for bar in bars:
        candidates = [bar.high - bar.low]
        if previous_close is not None:
            candidates.extend([abs(bar.high - previous_close), abs(bar.low - previous_close)])
        ranges.append(max(candidates))
        if len(ranges) >= period:
            output.append(sum(ranges[-period:]) / period)
        else:
            output.append(None)
        previous_close = bar.close
    return output


def vwap(bars: list[Bar]) -> list[float | None]:
    """Cumulative VWAP from typical-price volume."""

    output: list[float | None] = []
    cumulative_volume = 0.0
    cumulative_value = 0.0
    for bar in bars:
        typical = (bar.high + bar.low + bar.close) / 3
        cumulative_volume += bar.volume
        cumulative_value += typical * bar.volume
        output.append(cumulative_value / cumulative_volume if cumulative_volume else None)
    return output
