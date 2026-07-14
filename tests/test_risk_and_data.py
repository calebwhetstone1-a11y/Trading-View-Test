from datetime import datetime, time, timezone

from futures_backtester.data import filter_session
from futures_backtester.models import BacktestSettings, Bar
from futures_backtester.risk import DailyLossLimiter, TrailingDrawdown


def test_trailing_drawdown_stops_moving_at_threshold():
    dd = TrailingDrawdown(50_000, 2_500, stop_trailing_at_balance=51_000)
    dd.update(50_750)
    assert dd.floor == 48_250
    dd.update(52_000)
    assert dd.floor == 48_500
    assert dd.breached(48_500)


def test_daily_loss_limit_locks_after_breach():
    limiter = DailyLossLimiter(1_000)
    limiter.record(-999)
    assert not limiter.locked
    limiter.record(-1)
    assert limiter.locked


def test_timezone_session_filtering():
    settings = BacktestSettings(
        starting_balance=50_000,
        contracts=1,
        slippage_ticks=1,
        session_start=time(9, 30),
        session_end=time(16, 0),
        timezone="America/New_York",
    )
    bars = [
        Bar(datetime(2024, 1, 2, 14, 0, tzinfo=timezone.utc), 1, 1, 1, 1, 1),
        Bar(datetime(2024, 1, 2, 15, 0, tzinfo=timezone.utc), 2, 2, 2, 2, 1),
        Bar(datetime(2024, 1, 2, 22, 0, tzinfo=timezone.utc), 3, 3, 3, 3, 1),
    ]
    filtered = filter_session(bars, settings)
    assert [bar.open for bar in filtered] == [2]
    assert filtered[0].timestamp.tzinfo is not None
