import pytest

from app import config
from app.core.inflation import future_cost


def test_zero_years_returns_current_cost():
    assert future_cost(100000, 0) == 100000


def test_one_year_applies_six_percent():
    assert future_cost(100000, 1) == pytest.approx(106000)


def test_five_year_compounding():
    expected = 1000000 * (1 + config.INFLATION_RATE) ** 5
    assert future_cost(1000000, 5) == pytest.approx(expected)
    assert future_cost(1000000, 5) == pytest.approx(1338225.5776, rel=1e-9)
