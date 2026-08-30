import pytest

from app import config
from app.core.investment import monthly_saving_capacity, required_monthly_sip


def test_capacity_basic():
    assert monthly_saving_capacity(50000, 20) == pytest.approx(10000)


def test_capacity_zero_percent():
    assert monthly_saving_capacity(50000, 0) == 0


def test_sip_zero_years_guard_returns_full_amount():
    assert required_monthly_sip(500000, 0) == 500000


def test_sip_annuity_due_round_trip():
    # Investing the computed SIP at the start of each month must reach the target FV.
    target_fv = 1000000
    years = 5
    p = required_monthly_sip(target_fv, years)
    i = config.MONTHLY_RETURN_RATE
    n = years * 12
    fv = p * (((1 + i) ** n - 1) / i) * (1 + i)
    assert fv == pytest.approx(target_fv, rel=1e-9)


def test_sip_decreases_with_longer_horizon():
    assert required_monthly_sip(1000000, 10) < required_monthly_sip(1000000, 5)
