"""Performance metrics for completed trades and equity curves."""

from __future__ import annotations

import math

from futures_backtester.models import Trade


def max_consecutive(values: list[bool]) -> int:
    """Return longest consecutive True run."""

    best = current = 0
    for value in values:
        current = current + 1 if value else 0
        best = max(best, current)
    return best


def closed_equity_drawdown(equity: list[float]) -> float:
    """Maximum closed-equity drawdown in dollars."""

    if not equity:
        return 0.0
    peak = equity[0]
    drawdown = 0.0
    for value in equity:
        peak = max(peak, value)
        drawdown = max(drawdown, peak - value)
    return drawdown


def summarize_trades(trades: list[Trade]) -> dict[str, float | int]:
    """Compute core financial metrics from completed trades."""

    pnls = [trade.net_pnl for trade in trades]
    winners = [p for p in pnls if p > 0]
    losers = [p for p in pnls if p < 0]
    gross_profit = sum(winners)
    gross_loss = sum(losers)
    total = len(pnls)
    return {
        "total_trades": total,
        "wins": len(winners),
        "losses": len(losers),
        "win_percentage": len(winners) / total * 100 if total else 0.0,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "net_profit": sum(pnls),
        "profit_factor": gross_profit / abs(gross_loss) if gross_loss else math.inf,
        "average_trade": sum(pnls) / total if total else 0.0,
        "average_winner": gross_profit / len(winners) if winners else 0.0,
        "average_loser": gross_loss / len(losers) if losers else 0.0,
        "largest_winner": max(winners) if winners else 0.0,
        "largest_loser": min(losers) if losers else 0.0,
        "expected_value": sum(pnls) / total if total else 0.0,
        "maximum_consecutive_wins": max_consecutive([p > 0 for p in pnls]),
        "maximum_consecutive_losses": max_consecutive([p < 0 for p in pnls]),
    }
