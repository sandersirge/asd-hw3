"""
SurgeRule model tests (Homework Task 1).
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from rides.models import SurgeRule


START = datetime(2026, 1, 1, 18, 0, tzinfo=timezone.utc)
END = START + timedelta(hours=2)


def make_rule(**overrides):
    fields = {
        "label": "Evening rush",
        "starts_at": START,
        "ends_at": END,
        "multiplier": Decimal("1.5"),
    }
    fields.update(overrides)
    return SurgeRule(**fields)


# ---------------------------------------------------------------------------
# Window validation
# ---------------------------------------------------------------------------

def test_full_clean_rejects_ends_at_before_starts_at():
    rule = make_rule(ends_at=START - timedelta(minutes=1))

    with pytest.raises(ValidationError):
        rule.full_clean()


def test_full_clean_rejects_ends_at_equal_to_starts_at():
    rule = make_rule(ends_at=START)

    with pytest.raises(ValidationError):
        rule.full_clean()


def test_full_clean_accepts_ends_at_after_starts_at():
    rule = make_rule()

    rule.full_clean()  # must not raise