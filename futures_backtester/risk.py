"""Risk management and prop-firm drawdown helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class DailyLossLimiter:
    """Tracks realized daily P&L and signals lockout breaches."""

    daily_loss_limit: float
    daily_profit_limit: float | None = None
    realized_pnl: float = 0.0

    def __post_init__(self) -> None:
        if self.daily_loss_limit <= 0:
            raise ValueError("daily_loss_limit must be positive")

    def record(self, pnl: float) -> None:
        self.realized_pnl += pnl

    @property
    def locked(self) -> bool:
        if self.realized_pnl <= -abs(self.daily_loss_limit):
            return True
        return self.daily_profit_limit is not None and self.realized_pnl >= self.daily_profit_limit


@dataclass(slots=True)
class TrailingDrawdown:
    """Prop-firm trailing drawdown with optional stop-moving threshold."""

    starting_balance: float
    drawdown_amount: float
    stop_trailing_at_balance: float | None = None
    high_water_mark: float = field(init=False)
    floor: float = field(init=False)

    def __post_init__(self) -> None:
        if self.starting_balance <= 0 or self.drawdown_amount <= 0:
            raise ValueError("starting_balance and drawdown_amount must be positive")
        self.high_water_mark = self.starting_balance
        self.floor = self.starting_balance - self.drawdown_amount

    def update(self, equity: float) -> None:
        """Move the drawdown floor up when equity reaches a new high."""

        capped_equity = equity
        if self.stop_trailing_at_balance is not None:
            capped_equity = min(equity, self.stop_trailing_at_balance)
        if capped_equity > self.high_water_mark:
            self.high_water_mark = capped_equity
            self.floor = self.high_water_mark - self.drawdown_amount

    def breached(self, equity: float) -> bool:
        return equity <= self.floor
