"""
Cancellation flow — view-layer tests (Homework Task 2).
"""
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
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

@pytest.fixture
def in_progress_ride(accepted_ride):
    accepted_ride.start()
    return accepted_ride

@pytest.fixture
def completed_ride(in_progress_ride):
    in_progress_ride.complete()
    return in_progress_ride

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

# ---------------------------------------------------------------------------
# Owner GET — confirmation page
# ---------------------------------------------------------------------------

def test_owner_get_on_accepted_ride_renders_form(client, owner, accepted_ride):
    client.force_login(owner)

    response = client.get(cancel_url(accepted_ride))

    assert response.status_code == 200
    content = response.content.decode()
    assert "reason" in content
    assert accepted_ride.pickup_address in content


def test_owner_get_on_started_ride_redirects_with_message(
    client, owner, in_progress_ride
):
    client.force_login(owner)

    response = client.get(cancel_url(in_progress_ride))

    assert response.status_code == 302
    assert response.url == reverse("rides:dashboard")
    assert len(list(get_messages(response.wsgi_request))) == 1


def test_owner_get_on_completed_ride_redirects_with_message(
    client, owner, completed_ride
):
    client.force_login(owner)

    response = client.get(cancel_url(completed_ride))

    assert response.status_code == 302
    assert response.url == reverse("rides:dashboard")
    assert len(list(get_messages(response.wsgi_request))) == 1

# ---------------------------------------------------------------------------
# Owner POST — form validation
# ---------------------------------------------------------------------------

def test_owner_post_with_valid_reason_cancels_and_redirects(
    client, owner, accepted_ride
):
    client.force_login(owner)

    response = client.post(
        cancel_url(accepted_ride), {"reason": "Flat tire on the highway"}
    )

    assert response.status_code == 302
    assert response.url == reverse("rides:dashboard")
    accepted_ride.refresh_from_db()
    assert accepted_ride.status == Ride.STATUS_CANCELLED
    assert accepted_ride.cancellation_reason == "Flat tire on the highway"


def test_owner_post_stores_stripped_reason(client, owner, accepted_ride):
    client.force_login(owner)

    client.post(cancel_url(accepted_ride), {"reason": "   Flat tire   "})

    accepted_ride.refresh_from_db()
    assert accepted_ride.cancellation_reason == "Flat tire"


@pytest.mark.parametrize("bad_reason", [
    "abcd",            # too short
    "",                # empty
    "      ",          # whitespace only
    "   abcd   ",      # too short once stripped
    "x" * 501,         # too long
])
def test_owner_post_with_invalid_reason_rerenders_and_leaves_ride(
    client, owner, accepted_ride, bad_reason
):
    client.force_login(owner)

    response = client.post(cancel_url(accepted_ride), {"reason": bad_reason})

    assert response.status_code == 200
    assert "reason" in response.content.decode()
    accepted_ride.refresh_from_db()
    assert accepted_ride.status == Ride.STATUS_ACCEPTED
    assert accepted_ride.cancellation_reason == ""

# ---------------------------------------------------------------------------
# Dashboard — Cancel is a link to the confirmation page
# ---------------------------------------------------------------------------

def test_dashboard_links_to_cancel_page_for_accepted_ride(
    client, owner, accepted_ride
):
    client.force_login(owner)

    response = client.get(reverse("rides:dashboard"))

    assert response.status_code == 200
    assert f'href="{cancel_url(accepted_ride)}"' in response.content.decode()


def test_dashboard_has_no_form_posting_to_cancel_url(
    client, owner, accepted_ride
):
    client.force_login(owner)

    response = client.get(reverse("rides:dashboard"))

    assert response.status_code == 200
    assert f'action="{cancel_url(accepted_ride)}"' not in response.content.decode()


def test_dashboard_has_no_cancel_link_for_started_ride(
    client, owner, in_progress_ride
):
    client.force_login(owner)

    response = client.get(reverse("rides:dashboard"))

    assert response.status_code == 200
    assert cancel_url(in_progress_ride) not in response.content.decode()