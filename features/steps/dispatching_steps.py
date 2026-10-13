"""
Task 2 — step definitions for `driver_dispatching.feature`.

Tips:
    * Use `from django.contrib.auth.models import User` to create a driver.
    * After creating the user, log in with
      `context.client.login(username=..., password=...)`.
    * Use `context.client.post(url)` to hit the accept-ride view.
    * Resolve URLs with `from django.urls import reverse`.
    * Persist the ride object on `context.ride` so later steps can find it.

Recommended structure (uncomment as you implement):

    from behave import given, when, then
    from decimal import Decimal
    from django.contrib.auth.models import User
    from django.urls import reverse
    from rides.models import Ride


    @given('a driver named "{name}"')
    def step_create_driver(context, name):
        ...
"""

from decimal import Decimal
from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse
from rides.models import Ride

@given('a driver named "{name}"')
def step_create_driver(context, name):
    user = User.objects.create_user(username=name.lower(), password="testpass")
    context.client.login(username=user.username, password="testpass")
    context.driver = user

@given('a pending ride from "{pickup}" to "{dropoff}" of {distance:f} km')
def step_create_pending_ride(context, pickup, dropoff, distance):
    context.ride = Ride.objects.create(
        pickup_address=pickup,
        dropoff_address=dropoff,
        distance_km=Decimal(str(distance)),
    )

@when("{name} accepts the ride from her dashboard")
def step_accept_via_http(context, name):
    response = context.client.post(
        reverse("rides:accept", args=[context.ride.id])
    )
    assert response.status_code == 302

@then('the ride is "{status}"')
def step_impl(context, status):
    context.ride.refresh_from_db()
    assert context.ride.status == status

@then('the ride is assigned to "{name}"')
def step_impl(context, name):
    context.ride.refresh_from_db()
    assert context.ride.driver.username == name.lower()