"""Typed domain models for futures backtesting."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from enum import StrEnum
from typing import Literal


class TradeSide(StrEnum):
    """Supported trade directions."""

    LONG = "long"
    SHORT = "short"


@dataclass(frozen=True, slots=True)
class Bar:
    """Single OHLCV market-data bar with a timezone-aware timestamp."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __post_init__(self) -> None:
        if self.timestamp.tzinfo is None:
            raise ValueError("bar timestamp must be timezone-aware")
        if self.high < self.low:
            raise ValueError("bar high must be greater than or equal to low")
        if self.volume < 0:
            raise ValueError("bar volume cannot be negative")


@dataclass(frozen=True, slots=True)
class ContractSpec:
    """Configurable futures contract specification.

    Values are intentionally supplied by configuration so NQ/MNQ or any other
    instrument can be tested without hardcoded exchange specifications.
    """

    symbol: str
    point_value: float
    tick_size: float
    commission_per_contract: float

    def __post_init__(self) -> None:
        if self.point_value <= 0:
            raise ValueError("point_value must be positive")
        if self.tick_size <= 0:
            raise ValueError("tick_size must be positive")
        if self.commission_per_contract < 0:
            raise ValueError("commission_per_contract cannot be negative")


@dataclass(frozen=True, slots=True)
class BacktestSettings:
    """Top-level settings that control a backtest run."""

    starting_balance: float
    contracts: int
    slippage_ticks: float
    date_start: str | None = None
    date_end: str | None = None
    session_start: time = time(9, 30)
    session_end: time = time(16, 0)
    timezone: str = "America/New_York"

    def __post_init__(self) -> None:
        if self.starting_balance <= 0:
            raise ValueError("starting_balance must be positive")
        if self.contracts <= 0:
            raise ValueError("contracts must be positive")
        if self.slippage_ticks < 0:
            raise ValueError("slippage_ticks cannot be negative")


@dataclass(frozen=True, slots=True)
class StrategySettings:
    """Configurable strategy knobs for the initial engine implementation."""

    direction: Literal["long", "short", "both"] = "both"
    ema_fast: int = 9
    ema_slow: int = 21
    atr_period: int = 14
    relative_volume_period: int = 20
    use_vwap: bool = True
    stop_loss_points: float = 20.0
    profit_target_points: float = 40.0
    break_even_trigger_points: float | None = None
    trailing_stop_points: float | None = None
    max_trades_per_day: int = 3
    daily_loss_lockout: float | None = None
    daily_profit_lockout: float | None = None


@dataclass(frozen=True, slots=True)
class Trade:
    """A completed trade used by metrics, prop-firm simulation, and reports."""

    symbol: str
    side: TradeSide
    entry_time: object
    exit_time: object
    entry_price: float
    exit_price: float
    contracts: int
    gross_pnl: float
    commission: float
    slippage: float
    net_pnl: float
    exit_reason: str


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Application configuration without third-party validation dependencies."""

    contract: ContractSpec
    backtest: BacktestSettings
    strategy: StrategySettings = field(default_factory=StrategySettings)
    prop_firm: dict[str, object] = field(default_factory=dict)
    optimization: dict[str, object] = field(default_factory=dict)
