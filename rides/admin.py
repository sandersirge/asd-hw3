from django.contrib import admin

from .models import Ride


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = (
        "pickup_address",
        "dropoff_address",
        "distance_km",
        "fare",
        "status",
        "driver",
        "requested_at",
    )
    list_filter = ("status", "driver")
    search_fields = ("pickup_address", "dropoff_address")
