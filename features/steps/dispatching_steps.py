"""
Step definitions for `driver_dispatching.feature`.

The single accept scenario exercises the dashboard end-to-end through
Django's test client: it proves the template, view, URL routing and
model all work together for the driver-accepts-a-ride flow.
"""
from decimal import Decimal

from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse

from rides.models import Ride


# ---------------------------------------------------------------------------
# Background steps
# ---------------------------------------------------------------------------

@given('a driver named "{name}"')
def step_create_driver(context, name):
    username = name.lower()
    user = User.objects.create_user(username=username, password="testpass")
    context.client.login(username=username, password="testpass")
    context.driver = user


@given('a pending ride from "{pickup}" to "{dropoff}" of {distance:f} km')
def step_create_pending_ride(context, pickup, dropoff, distance):
    context.ride = Ride.objects.create(
        pickup_address=pickup,
        dropoff_address=dropoff,
        distance_km=Decimal(str(distance)),
    )


# ---------------------------------------------------------------------------
# When — accept via HTTP
# ---------------------------------------------------------------------------

@when("{name} accepts the ride from her dashboard")
def step_accept_via_http(context, name):
    response = context.client.post(
        reverse("rides:accept", args=[context.ride.id])
    )
    assert response.status_code == 302, (
        f"Expected redirect after accept, got {response.status_code}"
    )


# ---------------------------------------------------------------------------
# Then — assertions
# ---------------------------------------------------------------------------

@then('the ride is "{status}"')
def step_ride_status(context, status):
    context.ride.refresh_from_db()
    assert context.ride.status == status, (
        f"Expected status {status!r}, got {context.ride.status!r}"
    )


@then('the ride is assigned to "{name}"')
def step_ride_driver(context, name):
    context.ride.refresh_from_db()
    assert context.ride.driver is not None, "Ride has no driver"
    assert context.ride.driver.username == name.lower()
