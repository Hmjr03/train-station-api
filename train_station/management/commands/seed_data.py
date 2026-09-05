from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from train_station.models import (
    Crew,
    Journey,
    Route,
    Station,
    Train,
    TrainType,
)


class Command(BaseCommand):
    help = "Create demonstration data for the Train Station API"

    def handle(self, *args, **options):
        milan, _ = Station.objects.get_or_create(
            name="Milano Centrale",
            defaults={
                "latitude": 45.4863,
                "longitude": 9.2047,
            },
        )

        rome, _ = Station.objects.get_or_create(
            name="Roma Termini",
            defaults={
                "latitude": 41.9010,
                "longitude": 12.5018,
            },
        )

        florence, _ = Station.objects.get_or_create(
            name="Firenze Santa Maria Novella",
            defaults={
                "latitude": 43.7765,
                "longitude": 11.2478,
            },
        )

        venice, _ = Station.objects.get_or_create(
            name="Venezia Santa Lucia",
            defaults={
                "latitude": 45.4411,
                "longitude": 12.3210,
            },
        )

        high_speed, _ = TrainType.objects.get_or_create(
            name="High Speed",
        )

        intercity, _ = TrainType.objects.get_or_create(
            name="Intercity",
        )

        frecciarossa, _ = Train.objects.get_or_create(
            name="Frecciarossa 1000",
            defaults={
                "cargo_num": 8,
                "places_in_cargo": 50,
                "train_type": high_speed,
            },
        )

        intercity_train, _ = Train.objects.get_or_create(
            name="Intercity 550",
            defaults={
                "cargo_num": 6,
                "places_in_cargo": 40,
                "train_type": intercity,
            },
        )

        milan_rome, _ = Route.objects.get_or_create(
            source=milan,
            destination=rome,
            defaults={
                "distance": 570,
            },
        )

        milan_venice, _ = Route.objects.get_or_create(
            source=milan,
            destination=venice,
            defaults={
                "distance": 267,
            },
        )

        florence_rome, _ = Route.objects.get_or_create(
            source=florence,
            destination=rome,
            defaults={
                "distance": 274,
            },
        )

        crew_one, _ = Crew.objects.get_or_create(
            first_name="Alessandro",
            last_name="Rossi",
        )

        crew_two, _ = Crew.objects.get_or_create(
            first_name="Giulia",
            last_name="Bianchi",
        )

        crew_three, _ = Crew.objects.get_or_create(
            first_name="Marco",
            last_name="Romano",
        )

        now = timezone.now()

        journey_one, created = Journey.objects.get_or_create(
            route=milan_rome,
            train=frecciarossa,
            defaults={
                "departure_time": now + timedelta(days=1, hours=2),
                "arrival_time": now + timedelta(days=1, hours=5),
            },
        )

        if created:
            journey_one.crew.set(
                [
                    crew_one,
                    crew_two,
                ]
            )

        journey_two, created = Journey.objects.get_or_create(
            route=milan_venice,
            train=intercity_train,
            defaults={
                "departure_time": now + timedelta(days=2, hours=3),
                "arrival_time": now + timedelta(days=2, hours=6),
            },
        )

        if created:
            journey_two.crew.set(
                [
                    crew_two,
                    crew_three,
                ]
            )

        journey_three, created = Journey.objects.get_or_create(
            route=florence_rome,
            train=frecciarossa,
            defaults={
                "departure_time": now + timedelta(days=3, hours=1),
                "arrival_time": now + timedelta(days=3, hours=3),
            },
        )

        if created:
            journey_three.crew.set(
                [
                    crew_one,
                    crew_three,
                ]
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data created successfully."
            )
        )
