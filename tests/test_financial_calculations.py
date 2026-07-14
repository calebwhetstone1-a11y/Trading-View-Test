from futures_backtester.execution import commission_amount, gross_pnl, intrabar_stop_target, net_pnl, slippage_amount
from futures_backtester.models import ContractSpec, TradeSide


def nq():
    return ContractSpec("NQ", point_value=20.0, tick_size=0.25, commission_per_contract=2.5)


def mnq():
    return ContractSpec("MNQ", point_value=2.0, tick_size=0.25, commission_per_contract=0.5)


def test_long_nq_pnl():
    assert gross_pnl(TradeSide.LONG, 18000, 18010, nq(), 1) == 200


def test_short_mnq_pnl():
    assert gross_pnl(TradeSide.SHORT, 18010, 18000, mnq(), 2) == 40


def test_commissions_and_slippage_reduce_net_pnl():
    contract = nq()
    assert commission_amount(contract, 2) == 10
    assert slippage_amount(contract, 2, 1) == 10
    assert net_pnl(TradeSide.LONG, 100, 101, contract, 2, 1) == 10


def test_intrabar_long_stop_before_target_when_both_hit():
    decision = intrabar_stop_target(TradeSide.LONG, bar_high=110, bar_low=90, stop_price=95, target_price=108)
    assert decision.exit_price == 95
    assert decision.reason == "stop_loss"


def test_intrabar_short_target():
    decision = intrabar_stop_target(TradeSide.SHORT, bar_high=101, bar_low=94, stop_price=105, target_price=95)
    assert decision.exit_price == 95
    assert decision.reason == "profit_target"
