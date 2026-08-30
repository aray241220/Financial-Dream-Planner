from app.core.feasibility import (
    ACHIEVABLE,
    CHALLENGING,
    HIGHLY_CHALLENGING,
    classify,
)


def test_surplus_is_achievable():
    assert classify(10000, 8000) == ACHIEVABLE


def test_exact_break_even_is_achievable():
    assert classify(10000, 10000) == ACHIEVABLE


def test_small_shortfall_is_challenging():
    assert classify(10000, 12000) == CHALLENGING


def test_shortfall_at_25_percent_boundary_is_challenging():
    assert classify(10000, 12500) == CHALLENGING


def test_shortfall_just_over_boundary_is_highly_challenging():
    assert classify(10000, 12501) == HIGHLY_CHALLENGING


def test_zero_capacity_with_requirement_is_highly_challenging():
    assert classify(0, 5000) == HIGHLY_CHALLENGING


def test_zero_capacity_zero_requirement_is_achievable():
    assert classify(0, 0) == ACHIEVABLE
