"""
Step definitions for `receipt.feature`.

Steps stay declarative: the scenario says *what* the driver does, the
step code decides *how* (HTTP calls through Django's test client).
"""
import re

from behave import given, when, then
from django.contrib.auth.models import User
from django.urls import reverse


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


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------

@when("{name} completes the ride")
def step_completes(context, name):
    context.response = context.client.post(
        reverse("rides:complete", args=[context.ride.id]), follow=True
    )


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