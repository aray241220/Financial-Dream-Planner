"""Inflation-adjusted future cost of a goal (fixed 6% annual)."""
from __future__ import annotations

from app import config


def future_cost(current_cost: float, years: float) -> float:
    """Future Cost = Current Cost * (1 + inflation) ** years."""
    return current_cost * (1 + config.INFLATION_RATE) ** years
