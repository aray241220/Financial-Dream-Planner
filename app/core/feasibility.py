"""Classify a plan as Achievable / Challenging / Highly Challenging."""
from __future__ import annotations

from app import config

ACHIEVABLE = "Achievable"
CHALLENGING = "Challenging"
HIGHLY_CHALLENGING = "Highly Challenging"


def classify(capacity: float, required: float) -> str:
    """Compare monthly capacity vs required investment and label feasibility."""
    surplus = capacity - required
    if surplus >= 0:
        return ACHIEVABLE
    shortfall = -surplus
    if shortfall <= config.CHALLENGING_SHORTFALL_RATIO * capacity:
        return CHALLENGING
    return HIGHLY_CHALLENGING
