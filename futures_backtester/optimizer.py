"""Optimization scaffolding for grid, random, and walk-forward workflows."""

from __future__ import annotations

from itertools import product
from typing import Any, Iterable


def grid_parameters(search_space: dict[str, Iterable[Any]]) -> list[dict[str, Any]]:
    """Expand a grid-search parameter dictionary into run dictionaries."""
    keys = list(search_space)
    return [dict(zip(keys, values, strict=True)) for values in product(*(search_space[k] for k in keys))]
