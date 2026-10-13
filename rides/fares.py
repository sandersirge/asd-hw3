"""
Fare-calculation helpers — pre-built and already tested.

This module is provided as-is so the app runs out of the box. You do not
need to modify it during the lab (Task 1 is the ride lifecycle in
rides/models.py). You will extend this function in the homework.

Tasko's pricing rules:
    fare = max(BASE_FARE + PER_KM_RATE * distance_km, MIN_FARE)

We use Decimal everywhere because float arithmetic on money silently loses
cents. `Decimal(str(value))` is the safe way to convert from a float without
inheriting its binary-representation noise.
"""
from decimal import Decimal


BASE_FARE = Decimal("2.50")
PER_KM_RATE = Decimal("1.20")
MIN_FARE = Decimal("4.00")
_CENTS = Decimal("0.01")


def calculate_fare(distance_km):
    """Return the fare in euros for a trip of `distance_km` kilometres.

    Args:
        distance_km: an int, float or Decimal — the trip distance.

    Returns:
        Decimal: the fare rounded to two decimal places.

    Raises:
        TypeError:  if `distance_km` is not a number (or is a bool).
        ValueError: if `distance_km` is negative.
    """
    # bool is a subclass of int in Python — reject it explicitly so a vote
    # of `True` is not silently treated as 1 km.
    if isinstance(distance_km, bool):
        raise TypeError("distance_km cannot be a bool")
    if not isinstance(distance_km, (int, float, Decimal)):
        raise TypeError(
            f"distance_km must be a number, got {type(distance_km).__name__}"
        )

    distance = Decimal(str(distance_km))
    if distance < 0:
        raise ValueError("distance_km cannot be negative")

    raw = BASE_FARE + PER_KM_RATE * distance
    return max(raw, MIN_FARE).quantize(_CENTS)
