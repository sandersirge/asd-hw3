"""
Seed the development database with two demo drivers and a handful of pending
rides so students can poke at the dashboard before they start coding.
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from rides.models import Ride


SAMPLE_RIDES = [
    ("Raekoja plats, Tartu",        "Tartu Airport",                7.4),
    ("Lossi 3, Tartu",              "Eedeni keskus",                3.2),
    ("Annelinn",                    "Tartu \u00dclikooli peahoone", 4.6),
    ("Tasku keskus",                "Anne kanal",                   2.1),
]


class Command(BaseCommand):
    help = "Create two demo drivers and a few pending ride requests."

    def handle(self, *args, **options):
        created_users = 0
        for username in ("mari", "anna"):
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": username.capitalize()},
            )
            if created:
                user.set_password("tasko123")
                user.save()
                created_users += 1

        created_rides = 0
        for pickup, dropoff, distance in SAMPLE_RIDES:
            ride, created = Ride.objects.get_or_create(
                pickup_address=pickup,
                dropoff_address=dropoff,
                defaults={
                    "distance_km": Decimal(str(distance)),
                    "status": Ride.STATUS_REQUESTED,
                },
            )
            if created:
                created_rides += 1

        self.stdout.write(self.style.SUCCESS(
            f"seed_demo done: {created_users} new driver(s), "
            f"{created_rides} new ride(s)."
        ))
