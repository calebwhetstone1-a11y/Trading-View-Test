"""Execution and financial calculation utilities."""

from __future__ import annotations

from dataclasses import dataclass

from futures_backtester.models import ContractSpec, TradeSide


@dataclass(frozen=True, slots=True)
class ExitDecision:
    """Intrabar stop/target exit result."""

    exit_price: float | None
    reason: str | None


def slippage_amount(contract: ContractSpec, contracts: int, slippage_ticks: float) -> float:
    """Return dollar slippage for one fill."""

    if contracts <= 0:
        raise ValueError("contracts must be positive")
    if slippage_ticks < 0:
        raise ValueError("slippage_ticks cannot be negative")
    return slippage_ticks * contract.tick_size * contract.point_value * contracts


def commission_amount(contract: ContractSpec, contracts: int, round_turn: bool = True) -> float:
    """Return commission in dollars for the requested contract count."""

    if contracts <= 0:
        raise ValueError("contracts must be positive")
    multiplier = 2 if round_turn else 1
    return contract.commission_per_contract * contracts * multiplier


def gross_pnl(side: TradeSide, entry_price: float, exit_price: float, contract: ContractSpec, contracts: int) -> float:
    """Calculate futures trade gross P&L before costs."""

    if contracts <= 0:
        raise ValueError("contracts must be positive")
    points = exit_price - entry_price if side == TradeSide.LONG else entry_price - exit_price
    return points * contract.point_value * contracts


def net_pnl(
    side: TradeSide,
    entry_price: float,
    exit_price: float,
    contract: ContractSpec,
    contracts: int,
    slippage_ticks: float,
) -> float:
    """Calculate round-turn net P&L after commissions and two slippage fills."""

    gross = gross_pnl(side, entry_price, exit_price, contract, contracts)
    costs = commission_amount(contract, contracts) + 2 * slippage_amount(contract, contracts, slippage_ticks)
    return gross - costs


def intrabar_stop_target(
    side: TradeSide,
    bar_high: float,
    bar_low: float,
    stop_price: float,
    target_price: float,
) -> ExitDecision:
    """Resolve whether an OHLC bar hits a stop or target.

    If both stop and target are touched in the same bar, the conservative choice
    is used: stop first. This avoids overstating performance with unknowable
    intrabar ordering.
    """

    if bar_high < bar_low:
        raise ValueError("bar_high must be greater than or equal to bar_low")
    if side == TradeSide.LONG:
        if bar_low <= stop_price:
            return ExitDecision(stop_price, "stop_loss")
        if bar_high >= target_price:
            return ExitDecision(target_price, "profit_target")
    else:
        if bar_high >= stop_price:
            return ExitDecision(stop_price, "stop_loss")
        if bar_low <= target_price:
            return ExitDecision(target_price, "profit_target")
    return ExitDecision(None, None)
