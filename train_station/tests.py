from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from train_station.models import (
    Journey,
    Route,
    Station,
    Ticket,
    Train,
    TrainType,
)


class TrainStationAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="traveler",
            email="traveler@example.com",
            password="StrongPassword123!",
        )

        self.source = Station.objects.create(
            name="Milano Centrale",
            latitude=45.4863,
            longitude=9.2047,
        )

        self.destination = Station.objects.create(
            name="Roma Termini",
            latitude=41.9010,
            longitude=12.5018,
        )

        self.route = Route.objects.create(
            source=self.source,
            destination=self.destination,
            distance=570,
        )

        self.train_type = TrainType.objects.create(
            name="High Speed",
        )

        self.train = Train.objects.create(
            name="Frecciarossa 1000",
            cargo_num=8,
            places_in_cargo=50,
            train_type=self.train_type,
        )

        departure_time = timezone.now() + timedelta(days=1)

        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=departure_time,
            arrival_time=departure_time + timedelta(hours=3),
        )

    def test_station_list_is_public(self):
        response = self.client.get(
            reverse("train_station:station-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_orders_require_authentication(self):
        response = self.client.get(
            reverse("train_station:order-list")
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_can_create_order(self):
        self.client.force_authenticate(self.user)

        payload = {
            "tickets": [
                {
                    "journey": self.journey.id,
                    "cargo": 1,
                    "seat": 1,
                }
            ]
        }

        response = self.client.post(
            reverse("train_station:order-list"),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            Ticket.objects.count(),
            1,
        )

        ticket = Ticket.objects.first()

        self.assertEqual(ticket.order.user, self.user)

    def test_cannot_book_existing_seat(self):
        self.client.force_authenticate(self.user)

        first_payload = {
            "tickets": [
                {
                    "journey": self.journey.id,
                    "cargo": 1,
                    "seat": 10,
                }
            ]
        }

        self.client.post(
            reverse("train_station:order-list"),
            first_payload,
            format="json",
        )

        second_response = self.client.post(
            reverse("train_station:order-list"),
            first_payload,
            format="json",
        )

        self.assertEqual(
            second_response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_book_invalid_seat(self):
        self.client.force_authenticate(self.user)

        payload = {
            "tickets": [
                {
                    "journey": self.journey.id,
                    "cargo": 1,
                    "seat": 999,
                }
            ]
        }

        response = self.client.post(
            reverse("train_station:order-list"),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_book_duplicate_seat_in_same_order(self):
        self.client.force_authenticate(self.user)

        payload = {
            "tickets": [
                {
                    "journey": self.journey.id,
                    "cargo": 2,
                    "seat": 5,
                },
                {
                    "journey": self.journey.id,
                    "cargo": 2,
                    "seat": 5,
                },
            ]
        }

        response = self.client.post(
            reverse("train_station:order-list"),
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Ticket.objects.count(),
            0,
        )

    def test_journey_can_be_filtered_by_source(self):
        response = self.client.get(
            reverse("train_station:journey-list"),
            {
                "source": "Milano",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )

    def test_journey_can_be_filtered_by_destination(self):
        response = self.client.get(
            reverse("train_station:journey-list"),
            {
                "destination": "Roma",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )
