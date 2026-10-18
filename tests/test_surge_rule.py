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

# ---------------------------------------------------------------------------
# Multiplier validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad", ["0.50", "1.10", "1.30", "2.25", "2.50", "3.00"])
def test_full_clean_rejects_non_canonical_multiplier(bad):
    rule = make_rule(multiplier=Decimal(bad))

    with pytest.raises(ValidationError):
        rule.full_clean()


@pytest.mark.parametrize("good", ["1.0", "1.25", "1.5", "1.75", "2.0"])
def test_full_clean_accepts_canonical_multiplier(good):
    rule = make_rule(multiplier=Decimal(good))

    rule.full_clean()  # must not raise

# ---------------------------------------------------------------------------
# covers(when) — half-open window [starts_at, ends_at)
# ---------------------------------------------------------------------------

def test_covers_is_inclusive_at_start():
    assert make_rule().covers(START) is True


def test_covers_is_exclusive_at_end():
    assert make_rule().covers(END) is False


def test_covers_moment_inside_window():
    assert make_rule().covers(START + timedelta(hours=1)) is True


def test_covers_last_moment_before_end():
    assert make_rule().covers(END - timedelta(microseconds=1)) is True


def test_covers_rejects_moment_before_start():
    assert make_rule().covers(START - timedelta(microseconds=1)) is False


def test_covers_rejects_moment_after_end():
    assert make_rule().covers(END + timedelta(minutes=1)) is False