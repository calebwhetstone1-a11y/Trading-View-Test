from futures_backtester.config import load_config


def test_load_example_yaml_without_third_party_dependencies():
    config = load_config("configs/example.yaml")
    assert config.contract.symbol == "NQ"
    assert config.contract.point_value == 20.0
    assert config.backtest.timezone == "America/New_York"
    assert config.strategy.direction == "both"
