"""
Fare calculator tests (pre-built for students).
"""
from decimal import Decimal

import pytest

from rides.fares import calculate_fare


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("distance,expected", [
    (0,                        Decimal("4.00")),   # min-fare floor
    (1,                        Decimal("4.00")),   # 3.70 rounded up to floor
    (Decimal("1.25"),          Decimal("4.00")),   # boundary: raw == floor
    (2,                        Decimal("4.90")),
    (5,                        Decimal("8.50")),
    (10,                       Decimal("14.50")),
    (Decimal("3.5"),           Decimal("6.70")),
])
def test_fare_for_valid_distances(distance, expected):
    assert calculate_fare(distance) == expected


def test_one_kilometre_just_above_boundary():
    """raw = 2.50 + 1.20*1.26 = 4.012 → rounded to 4.01 → above floor."""
    assert calculate_fare(Decimal("1.26")) == Decimal("4.01")


# ---------------------------------------------------------------------------
# Negative distances
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", [-1, -0.5, Decimal("-3")])
def test_negative_distance_raises_value_error(bad):
    with pytest.raises(ValueError):
        calculate_fare(bad)


# ---------------------------------------------------------------------------
# Non-numeric types
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_type", [None, "5", [1], object()])
def test_non_numeric_type_raises_type_error(bad_type):
    with pytest.raises(TypeError):
        calculate_fare(bad_type)


# ---------------------------------------------------------------------------
# The bool gotcha — bool is a subclass of int in Python
# ---------------------------------------------------------------------------

def test_bool_true_is_rejected():
    with pytest.raises(TypeError):
        calculate_fare(True)


def test_bool_false_is_rejected():
    with pytest.raises(TypeError):
        calculate_fare(False)


# ---------------------------------------------------------------------------
# Return-type contract
# ---------------------------------------------------------------------------

def test_result_is_always_a_decimal():
    assert isinstance(calculate_fare(0), Decimal)
    assert isinstance(calculate_fare(1.5), Decimal)
    assert isinstance(calculate_fare(Decimal("3")), Decimal)


def test_result_is_quantised_to_two_places():
    """3.333 km → raw = 6.4996 → must round to 6.50, not 6.4996."""
    assert calculate_fare(Decimal("3.333")) == Decimal("6.50")
