"""
Task 1 — TDD with PyTest-Django: Ride lifecycle.

You will drive four lifecycle methods into `rides/models.py` using TDD:

    1.  accept(driver)    — REQUESTED      → ACCEPTED;     assigns driver.
    2.  start()           — ACCEPTED       → IN_PROGRESS.
    3.  complete()        — IN_PROGRESS    → COMPLETED;    sets completed_at.
    4.  cancel(reason)    — REQUESTED|ACCEPTED → CANCELLED; stores reason.

Every illegal transition (e.g. completing a requested ride) must raise the
custom InvalidTransition exception that lives in `rides.models`.

Mark every test that touches the database with @pytest.mark.django_db so
PyTest-Django creates an isolated test database for you.
"""

from decimal import Decimal
import pytest
from django.contrib.auth.models import User
from rides.models import InvalidTransition, Ride


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
