"""Monthly saving capacity and the SIP required to reach a goal.

Investment return is a documented assumption (see config), not a guarantee.
Contributions are treated as start-of-month (annuity-due).
"""
from __future__ import annotations

from app import config


def monthly_saving_capacity(monthly_salary: float, saving_percentage: float) -> float:
    """Capacity = salary * saving_percentage / 100 (percentage is 0-100)."""
    return monthly_salary * (saving_percentage / 100.0)


def required_monthly_sip(future_value: float, years: float) -> float:
    """Monthly annuity-due contribution needed to reach future_value.

    P = (FV * i) / (((1 + i) ** n - 1) * (1 + i)),  i = monthly rate, n = months.
    """
    i = config.MONTHLY_RETURN_RATE
    n = int(round(years * 12))
    if n <= 0:
        return future_value  # cannot spread over zero months: full amount now
    if i == 0:
        return future_value / n
    growth = (1 + i) ** n
    return (future_value * i) / ((growth - 1) * (1 + i))
