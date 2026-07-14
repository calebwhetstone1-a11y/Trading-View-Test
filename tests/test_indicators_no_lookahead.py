from datetime import datetime
from zoneinfo import ZoneInfo

from futures_backtester.models import Bar, StrategySettings
from futures_backtester.strategy import generate_signals


def test_signals_do_not_use_current_bar_for_indicator_cross():
    tz = ZoneInfo("America/New_York")
    bars = [
        Bar(datetime(2024, 1, 1, 9, 30 + index, tzinfo=tz), value, value, value, value, 1)
        for index, value in enumerate([10, 10, 10, 100])
    ]
    signals = generate_signals(bars, StrategySettings(ema_fast=2, ema_slow=3))
    assert signals[-1] is None
