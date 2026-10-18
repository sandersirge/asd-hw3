from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import InvalidTransition, Ride


@login_required
def dashboard(request):
    """Driver dashboard: pending requests + my active rides."""
    pending = Ride.objects.filter(status=Ride.STATUS_REQUESTED)
    mine = Ride.objects.filter(driver=request.user).exclude(
        status__in=[Ride.STATUS_COMPLETED, Ride.STATUS_CANCELLED]
    )
    return render(
        request,
        "rides/dashboard.html",
        {"pending": pending, "mine": mine},
    )


@login_required
@require_POST
def accept_ride(request, ride_id):
    """Accept a pending ride — assigns it to the current driver."""
    ride = get_object_or_404(Ride, pk=ride_id)
    try:
        ride.accept(request.user)
    except (AttributeError, InvalidTransition) as exc:
        # AttributeError: students have not yet implemented Ride.accept()
        #   — the action becomes a no-op until they do.
        # InvalidTransition: the ride is no longer in the requested state.
        messages.error(request, _friendly_error(exc, "accept"))
    return redirect(reverse("rides:dashboard"))


@login_required
@require_POST
def start_ride(request, ride_id):
    """Start a ride that the current driver has accepted."""
    ride = _get_own_ride(request, ride_id)
    try:
        ride.start()
    except (AttributeError, InvalidTransition) as exc:
        messages.error(request, _friendly_error(exc, "start"))
    return redirect(reverse("rides:dashboard"))


@login_required
@require_POST
def complete_ride(request, ride_id):
    """Complete a ride that the current driver is in_progress on."""
    ride = _get_own_ride(request, ride_id)
    try:
        ride.complete()
    except (AttributeError, InvalidTransition) as exc:
        messages.error(request, _friendly_error(exc, "complete"))
    return redirect(reverse("rides:dashboard"))


@login_required
@require_POST
def cancel_ride(request, ride_id):
    """Cancel a ride the current driver owns (in any cancellable state)."""
    ride = _get_own_ride(request, ride_id)
    reason = request.POST.get("reason", "").strip() or "Cancelled by driver"
    try:
        ride.cancel(reason)
    except (AttributeError, InvalidTransition) as exc:
        messages.error(request, _friendly_error(exc, "cancel"))
    return redirect(reverse("rides:dashboard"))


@login_required
def ride_detail(request, ride_id):
    """Show a single ride."""
    ride = get_object_or_404(Ride, pk=ride_id)
    return render(request, "rides/detail.html", {"ride": ride})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_own_ride(request, ride_id):
    """Look up a ride that belongs to the current driver, else raise 404."""
    ride = get_object_or_404(Ride, pk=ride_id)
    if ride.driver_id != request.user.id:
        raise Http404("Ride not found")
    return ride


def _friendly_error(exc, action):
    """Turn a low-level error into a message a driver can read."""
    if isinstance(exc, AttributeError):
        return (
            f"Could not {action} the ride yet — the lifecycle method "
            f"has not been implemented."
        )
    return f"Could not {action} the ride: {exc}"
