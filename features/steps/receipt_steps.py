"""
Step definitions for `receipt.feature`.

Steps stay declarative: the scenario says *what* the driver does, the
step code decides *how* (HTTP calls through Django's test client).
"""
import re
from datetime import timedelta
from decimal import Decimal

from behave import given, when, then
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from rides.models import Ride, SurgeRule


def receipt_path(ride):
    """The receipt URL as fixed by the spec: /rides/<id>/receipt/."""
    return f"/rides/{ride.id}/receipt/"


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given("{name} has started the ride")
def step_has_started(context, name):
    driver = User.objects.get(username=name.lower())
    context.ride.accept(driver)
    context.ride.start()

@given("a {multiplier}× surge is active")
def step_surge_active(context, multiplier):
    now = timezone.now()
    SurgeRule.objects.create(
        label="Scenario surge",
        starts_at=now - timedelta(hours=1),
        ends_at=now + timedelta(hours=1),
        multiplier=Decimal(multiplier),
    )

@given("{name} has completed the ride")
def step_has_completed(context, name):
    step_has_started(context, name)
    context.ride.complete()

@given("{name} also has another ride in progress")
def step_has_another_ride_in_progress(context, name):
    driver = User.objects.get(username=name.lower())
    context.other_ride = Ride.objects.create(
        pickup_address="Tartu Bus Station",
        dropoff_address="Lõunakeskus",
        distance_km=Decimal("3.00"),
    )
    context.other_ride.accept(driver)
    context.other_ride.start()

# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------

@when("{name} completes the ride")
def step_completes(context, name):
    context.response = context.client.post(
        reverse("rides:complete", args=[context.ride.id]), follow=True
    )

@when("{name} opens the receipt for the ride")
def step_opens_receipt(context, name):
    context.response = context.client.get(receipt_path(context.ride))

# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then("{name} sees the receipt for the ride")
def step_sees_receipt(context, name):
    assert context.response.status_code == 200, (
        f"Expected 200, got {context.response.status_code}"
    )
    landed_on = context.response.redirect_chain[-1][0]
    assert landed_on == receipt_path(context.ride), (
        f"Expected to land on {receipt_path(context.ride)}, got {landed_on}"
    )


@then('the receipt shows the {field} as "{value}"')
def step_receipt_shows(context, field, value):
    element_id = "receipt-" + field.replace(" ", "-")
    html = context.response.content.decode()
    pattern = rf'id="{element_id}"[^>]*>\s*{re.escape(value)}\s*<'
    assert re.search(pattern, html), (
        f'Expected #{element_id} to show "{value}"'
    )

@then("{name} gets a {status:d} response")
def step_gets_status(context, name, status):
    assert context.response.status_code == status, (
        f"Expected {status}, got {context.response.status_code}"
    )

@then('{name}\'s dashboard lists the ride under "{panel}"')
def step_dashboard_lists_ride(context, name, panel):
    html = context.client.get(reverse("rides:dashboard")).content.decode()
    assert panel in html, f'Dashboard has no "{panel}" panel'
    link = f'href="{receipt_path(context.ride)}"'
    assert link in html, f"Dashboard does not link to {receipt_path(context.ride)}"

@then("{name}'s ride still in progress has no receipt yet")
def step_unfinished_ride_has_no_receipt(context, name):
    response = context.client.get(receipt_path(context.other_ride))
    assert response.status_code == 302, (
        f"Expected a redirect, got {response.status_code}"
    )
    assert response.url == reverse("rides:dashboard"), (
        f"Expected redirect to the dashboard, got {response.url}"
    )
    flashed = list(get_messages(response.wsgi_request))
    assert len(flashed) == 1, f"Expected 1 flash message, got {len(flashed)}"