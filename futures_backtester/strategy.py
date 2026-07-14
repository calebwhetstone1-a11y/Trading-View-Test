"""Strategy signal interface and simple EMA/VWAP reference strategy."""

from __future__ import annotations

from futures_backtester.indicators import ema, vwap
from futures_backtester.models import Bar, StrategySettings, TradeSide


def _previous(values: list[float | None]) -> list[float | None]:
    """Shift a series by one bar to prevent look-ahead bias."""

    return [None, *values[:-1]]


def generate_signals(bars: list[Bar], settings: StrategySettings) -> list[TradeSide | None]:
    """Generate entry signals from completed prior bars only."""

    closes = [bar.close for bar in bars]
    fast = _previous(ema(closes, settings.ema_fast))
    slow = _previous(ema(closes, settings.ema_slow))
    session_vwap = _previous(vwap(bars))
    prior_close: list[float | None] = [None, *closes[:-1]]
    signals: list[TradeSide | None] = []
    for fast_value, slow_value, vwap_value, close_value in zip(fast, slow, session_vwap, prior_close, strict=True):
        if fast_value is None or slow_value is None or vwap_value is None or close_value is None:
            signals.append(None)
        elif settings.direction in {"long", "both"} and fast_value > slow_value and close_value > vwap_value:
            signals.append(TradeSide.LONG)
        elif settings.direction in {"short", "both"} and fast_value < slow_value and close_value < vwap_value:
            signals.append(TradeSide.SHORT)
        else:
            signals.append(None)
    return signals
