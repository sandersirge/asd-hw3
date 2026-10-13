"""
Domain model for Tasko.

The base `Ride` model is provided so the application runs out of the box.
You will extend it during Task 1 of the lab using TDD: write a failing test
in `tests/test_models.py` first, then add the corresponding behaviour here.
"""
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


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

    def accept(self, driver):
        if self.status != self.STATUS_REQUESTED:
            raise InvalidTransition(
                f"Cannot accept ride in status '{self.status}'."
            )
        self.driver = driver
        self.status = self.STATUS_ACCEPTED
        self.save(update_fields=["status", "driver"])

    def start(self):
        if self.status != self.STATUS_ACCEPTED:
            raise InvalidTransition(
                f"Cannot start ride in status '{self.status}'."
            )
        self.status = self.STATUS_IN_PROGRESS
        self.save(update_fields=["status"])

    def complete(self):
        if self.status != self.STATUS_IN_PROGRESS:
            raise InvalidTransition(
                f"Cannot complete ride in status '{self.status}'."
            )
        self.status = self.STATUS_COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at"])

    def cancel(self, reason):
        if self.status not in [self.STATUS_REQUESTED, self.STATUS_ACCEPTED]:
            raise InvalidTransition(
                f"Cannot cancel ride in status '{self.status}'."
            )
        self.status = self.STATUS_CANCELLED
        self.cancellation_reason = reason
        self.save(update_fields=["status", "cancellation_reason"])
