"""
Cancellation flow — view-layer tests (Homework Task 2).
"""
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from rides.models import Ride


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def owner(db):
    return User.objects.create_user(username="mari", password="x")


@pytest.fixture
def other_driver(db):
    return User.objects.create_user(username="anna", password="x")


@pytest.fixture
def accepted_ride(owner):
    ride = Ride.objects.create(
        pickup_address="Raekoja plats",
        dropoff_address="Tartu Airport",
        distance_km=Decimal("5.00"),
    )
    ride.accept(owner)
    return ride


def cancel_url(ride):
    return reverse("rides:cancel", args=[ride.id])


# ---------------------------------------------------------------------------
# Authentication & authorisation
# ---------------------------------------------------------------------------

def test_anonymous_get_redirects_to_login(client, accepted_ride):
    response = client.get(cancel_url(accepted_ride))

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


def test_anonymous_post_redirects_to_login_and_leaves_ride(client, accepted_ride):
    response = client.post(cancel_url(accepted_ride), {"reason": "Flat tire"})

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")
    accepted_ride.refresh_from_db()
    assert accepted_ride.status == Ride.STATUS_ACCEPTED


def test_other_driver_get_returns_404(client, other_driver, accepted_ride):
    client.force_login(other_driver)

    response = client.get(cancel_url(accepted_ride))

    assert response.status_code == 404


def test_other_driver_post_returns_404_and_leaves_ride(
    client, other_driver, accepted_ride
):
    client.force_login(other_driver)

    response = client.post(cancel_url(accepted_ride), {"reason": "Flat tire"})

    assert response.status_code == 404
    accepted_ride.refresh_from_db()
    assert accepted_ride.status == Ride.STATUS_ACCEPTED