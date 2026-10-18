"""
Ride lifecycle tests.
"""
from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from rides.models import InvalidTransition, Ride, SurgeRule

@pytest.fixture
def driver(db):
    return User.objects.create_user(username="mari", password="x")


@pytest.fixture
def requested_ride(db):
    return Ride.objects.create(
        pickup_address="Raekoja plats",
        dropoff_address="Tartu Airport",
        distance_km=Decimal("5.00"),
    )


# ======================================================================
# 1. accept(driver) tests
# ======================================================================

@pytest.mark.django_db
def test_accept_moves_requested_ride_to_accepted(requested_ride, driver):
    requested_ride.accept(driver)
    requested_ride.refresh_from_db()
    assert requested_ride.status == Ride.STATUS_ACCEPTED
    assert requested_ride.driver == driver


@pytest.mark.django_db
def test_accept_rejects_already_completed_ride(requested_ride, driver):
    requested_ride.accept(driver)
    requested_ride.start()
    requested_ride.complete()
    with pytest.raises(InvalidTransition):
        requested_ride.accept(driver)


# ======================================================================
# 2. start() tests
# ======================================================================

@pytest.mark.django_db
def test_start_moves_accepted_ride_to_in_progress(requested_ride, driver):
    requested_ride.accept(driver)
    requested_ride.start()
    requested_ride.refresh_from_db()
    assert requested_ride.status == Ride.STATUS_IN_PROGRESS


@pytest.mark.django_db
def test_start_rejects_ride_that_was_not_accepted(requested_ride):
    with pytest.raises(InvalidTransition):
        requested_ride.start()


# ======================================================================
# 3. complete() tests
# ======================================================================

@pytest.mark.django_db
def test_complete_moves_in_progress_ride_to_completed(requested_ride, driver):
    requested_ride.accept(driver)
    requested_ride.start()
    requested_ride.complete()
    requested_ride.refresh_from_db()
    assert requested_ride.status == Ride.STATUS_COMPLETED
    assert requested_ride.completed_at is not None


@pytest.mark.django_db
def test_complete_rejects_a_ride_that_was_never_started(requested_ride, driver):
    requested_ride.accept(driver)
    with pytest.raises(InvalidTransition):
        requested_ride.complete()

# ======================================================================
# 4. cancel(reason) tests
# ======================================================================

@pytest.mark.django_db
def test_cancel_moves_requested_ride_to_cancelled(requested_ride):
    requested_ride.cancel("Passenger cancelled before driver accepted")
    requested_ride.refresh_from_db()
    assert requested_ride.status == Ride.STATUS_CANCELLED
    assert requested_ride.cancellation_reason == "Passenger cancelled before driver accepted"


@pytest.mark.django_db
def test_cancel_moves_accepted_ride_to_cancelled(requested_ride, driver):
    requested_ride.accept(driver)
    requested_ride.cancel("Driver had a flat tire")
    requested_ride.refresh_from_db()
    assert requested_ride.status == Ride.STATUS_CANCELLED
    assert requested_ride.cancellation_reason == "Driver had a flat tire"


@pytest.mark.django_db
def test_cancel_rejects_in_progress_ride(requested_ride, driver):
    requested_ride.accept(driver)
    requested_ride.start()
    with pytest.raises(InvalidTransition):
        requested_ride.cancel("Too late to cancel")

# ---------------------------------------------------------------------------
# complete() — captures surge multiplier and final fare (Homework Task 1)
# ---------------------------------------------------------------------------

def _drive_to_in_progress(ride, driver):
    ride.accept(driver)
    ride.start()


def _surge_around_now(multiplier, start_offset, end_offset):
    now = timezone.now()
    return SurgeRule.objects.create(
        label="Test surge",
        starts_at=now + start_offset,
        ends_at=now + end_offset,
        multiplier=Decimal(multiplier),
    )


def test_complete_without_surge_stores_base_fare(requested_ride, driver):
    _drive_to_in_progress(requested_ride, driver)

    requested_ride.complete()

    requested_ride.refresh_from_db()
    assert requested_ride.surge_multiplier == Decimal("1.00")
    assert requested_ride.fare == Decimal("8.50")


def test_complete_during_surge_stores_multiplier_and_boosted_fare(
    requested_ride, driver
):
    _surge_around_now("1.5", timedelta(hours=-1), timedelta(hours=1))
    _drive_to_in_progress(requested_ride, driver)

    requested_ride.complete()

    requested_ride.refresh_from_db()
    assert requested_ride.surge_multiplier == Decimal("1.50")
    assert requested_ride.fare == Decimal("12.75")


def test_complete_after_surge_ended_stores_base_fare(requested_ride, driver):
    _surge_around_now("2.0", timedelta(hours=-3), timedelta(hours=-1))
    _drive_to_in_progress(requested_ride, driver)

    requested_ride.complete()

    requested_ride.refresh_from_db()
    assert requested_ride.surge_multiplier == Decimal("1.00")
    assert requested_ride.fare == Decimal("8.50")
