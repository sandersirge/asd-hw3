"""
Domain model for Tasko — TASK 2 reference solution.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class InvalidTransition(Exception):
    """Raised when a Ride is asked to perform an invalid state transition."""


class Ride(models.Model):
    STATUS_REQUESTED = "requested"
    STATUS_ACCEPTED = "accepted"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    pickup_address = models.CharField(max_length=200)
    dropoff_address = models.CharField(max_length=200)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    fare = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="rides",
    )
    cancellation_reason = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-requested_at"]

    def __str__(self):
        return f"{self.pickup_address} → {self.dropoff_address}"

    # ------------------------------------------------------------------
    # Lifecycle methods
    # ------------------------------------------------------------------

    def accept(self, driver):
        """REQUESTED → ACCEPTED. Assigns the driver."""
        if self.status != self.STATUS_REQUESTED:
            raise InvalidTransition(
                f"Cannot accept a ride in {self.status!r} state"
            )
        self.driver = driver
        self.status = self.STATUS_ACCEPTED
        self.save(update_fields=["driver", "status"])

    def start(self):
        """ACCEPTED → IN_PROGRESS."""
        if self.status != self.STATUS_ACCEPTED:
            raise InvalidTransition(
                f"Cannot start a ride in {self.status!r} state"
            )
        self.status = self.STATUS_IN_PROGRESS
        self.save(update_fields=["status"])

    def complete(self):
        """IN_PROGRESS → COMPLETED. Stamps completed_at."""
        if self.status != self.STATUS_IN_PROGRESS:
            raise InvalidTransition(
                f"Cannot complete a ride in {self.status!r} state"
            )
        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    def cancel(self, reason):
        """REQUESTED or ACCEPTED → CANCELLED. Stores reason."""
        if self.status not in (self.STATUS_REQUESTED, self.STATUS_ACCEPTED):
            raise InvalidTransition(
                f"Cannot cancel a ride in {self.status!r} state"
            )
        self.status = self.STATUS_CANCELLED
        self.cancellation_reason = reason
        self.save(update_fields=["status", "cancellation_reason"])

class SurgeRule(models.Model):
    """A time window during which fares are multiplied."""

    ALLOWED_MULTIPLIERS = (
        Decimal("1.0"),
        Decimal("1.25"),
        Decimal("1.5"),
        Decimal("1.75"),
        Decimal("2.0"),
    )

    label = models.CharField(max_length=50)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    multiplier = models.DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        ordering = ["starts_at"]

    def __str__(self):
        return f"{self.label} (×{self.multiplier})"

    def clean(self):
        super().clean()
        errors = {}
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "ends_at must be strictly after starts_at."
        if (
            self.multiplier is not None
            and self.multiplier not in self.ALLOWED_MULTIPLIERS
        ):
            allowed = ", ".join(str(m) for m in self.ALLOWED_MULTIPLIERS)
            errors["multiplier"] = f"multiplier must be one of: {allowed}."
        if errors:
            raise ValidationError(errors)

    def covers(self, when):
        """True if `when` falls in the half-open window [starts_at, ends_at)."""
        return self.starts_at <= when < self.ends_at