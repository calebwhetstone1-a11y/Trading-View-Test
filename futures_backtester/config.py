"""Configuration loading for JSON and simple YAML strategy files."""

from __future__ import annotations

import json
from datetime import time
from pathlib import Path
from typing import Any

from futures_backtester.models import AppConfig, BacktestSettings, ContractSpec, StrategySettings


def _parse_scalar(value: str) -> object:
    """Parse a small YAML scalar subset used by the example configuration."""

    cleaned = value.strip().strip("'\"")
    if cleaned.lower() in {"true", "false"}:
        return cleaned.lower() == "true"
    if cleaned.lower() in {"null", "none"}:
        return None
    try:
        return int(cleaned)
    except ValueError:
        try:
            return float(cleaned)
        except ValueError:
            return cleaned


def _load_simple_yaml(text: str) -> dict[str, Any]:
    """Load a conservative two-level YAML mapping without external packages."""

    root: dict[str, Any] = {}
    current_section: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section_name = line[:-1].strip()
            current_section = {}
            root[section_name] = current_section
            continue
        if current_section is None or ":" not in line:
            raise ValueError("Only simple two-level YAML mappings are supported without PyYAML")
        key, value = line.strip().split(":", 1)
        current_section[key.strip()] = _parse_scalar(value)
    return root


def _parse_hhmm(value: object) -> time:
    """Parse HH:MM time values from configuration."""

    if not isinstance(value, str):
        raise ValueError("session time must be HH:MM")
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError("session time must be HH:MM")
    hour, minute = (int(part) for part in parts)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("session time must be a valid HH:MM")
    return time(hour, minute)


def load_config(path: str | Path) -> AppConfig:
    """Load and validate an application configuration from JSON or simple YAML."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    text = config_path.read_text(encoding="utf-8")
    if config_path.suffix.lower() == ".json":
        payload = json.loads(text)
    elif config_path.suffix.lower() in {".yaml", ".yml"}:
        payload = _load_simple_yaml(text)
    else:
        raise ValueError("Configuration file must be .yaml, .yml, or .json")
    if not isinstance(payload, dict):
        raise ValueError("Configuration root must be a mapping/object")

    contract_data = dict(payload.get("contract", {}))
    backtest_data = dict(payload.get("backtest", {}))
    strategy_data = dict(payload.get("strategy", {}))
    contract = ContractSpec(
        symbol=str(contract_data["symbol"]),
        point_value=float(contract_data["point_value"]),
        tick_size=float(contract_data["tick_size"]),
        commission_per_contract=float(contract_data["commission_per_contract"]),
    )
    backtest = BacktestSettings(
        starting_balance=float(backtest_data["starting_balance"]),
        contracts=int(backtest_data["contracts"]),
        slippage_ticks=float(backtest_data["slippage_ticks"]),
        date_start=backtest_data.get("date_start"),
        date_end=backtest_data.get("date_end"),
        session_start=_parse_hhmm(backtest_data.get("session_start", "09:30")),
        session_end=_parse_hhmm(backtest_data.get("session_end", "16:00")),
        timezone=str(backtest_data.get("timezone", "America/New_York")),
    )
    strategy = StrategySettings(**strategy_data)
    return AppConfig(
        contract=contract,
        backtest=backtest,
        strategy=strategy,
        prop_firm=dict(payload.get("prop_firm", {})),
        optimization=dict(payload.get("optimization", {})),
    )
