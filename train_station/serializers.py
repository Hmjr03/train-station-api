from django.db import transaction
from rest_framework import serializers

from train_station.models import (
    Crew,
    Journey,
    Order,
    Route,
    Station,
    Ticket,
    Train,
    TrainType,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = (
            "id",
            "name",
            "latitude",
            "longitude",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )

    def validate(self, attrs):
        source = attrs.get(
            "source",
            getattr(self.instance, "source", None),
        )
        destination = attrs.get(
            "destination",
            getattr(self.instance, "destination", None),
        )

        if source == destination:
            raise serializers.ValidationError(
                "Source and destination stations must be different."
            )

        return attrs


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(
        source="source.name",
        read_only=True,
    )
    destination = serializers.CharField(
        source="destination.name",
        read_only=True,
    )


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = (
            "id",
            "name",
        )


class TrainSerializer(serializers.ModelSerializer):
    capacity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_num",
            "places_in_cargo",
            "train_type",
            "capacity",
        )


class TrainListSerializer(TrainSerializer):
    train_type = serializers.CharField(
        source="train_type.name",
        read_only=True,
    )


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
        )


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
        )

    def validate(self, attrs):
        departure_time = attrs.get(
            "departure_time",
            getattr(self.instance, "departure_time", None),
        )
        arrival_time = attrs.get(
            "arrival_time",
            getattr(self.instance, "arrival_time", None),
        )

        if (
            departure_time is not None
            and arrival_time is not None
            and arrival_time <= departure_time
        ):
            raise serializers.ValidationError(
                "Arrival time must be later than departure time."
            )

        return attrs


class JourneyListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(
        source="route.source.name",
        read_only=True,
    )
    destination = serializers.CharField(
        source="route.destination.name",
        read_only=True,
    )
    train = serializers.CharField(
        source="train.name",
        read_only=True,
    )
    tickets_available = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = (
            "id",
            "source",
            "destination",
            "train",
            "departure_time",
            "arrival_time",
            "tickets_available",
        )

    def get_tickets_available(self, obj):
        if hasattr(obj, "tickets_count"):
            tickets_count = obj.tickets_count
        else:
            tickets_count = obj.tickets.count()

        return obj.train.capacity - tickets_count


class JourneyDetailSerializer(serializers.ModelSerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainListSerializer(read_only=True)
    crew = CrewSerializer(
        many=True,
        read_only=True,
    )
    tickets_available = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
        )

    def get_tickets_available(self, obj):
        if hasattr(obj, "tickets_count"):
            tickets_count = obj.tickets_count
        else:
            tickets_count = obj.tickets.count()

        return obj.train.capacity - tickets_count


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "cargo",
            "seat",
            "journey",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        journey = attrs["journey"]
        cargo = attrs["cargo"]
        seat = attrs["seat"]

        Ticket.validate_ticket(
            cargo=cargo,
            seat=seat,
            train=journey.train,
            error_to_raise=serializers.ValidationError,
        )

        if Ticket.objects.filter(
            journey=journey,
            cargo=cargo,
            seat=seat,
        ).exists():
            raise serializers.ValidationError(
                "This seat is already booked for this journey."
            )

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True,
        allow_empty=False,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "tickets",
            "created_at",
        )
        read_only_fields = (
            "id",
            "created_at",
        )

    def validate_tickets(self, tickets):
        selected_seats = set()

        for ticket in tickets:
            seat_key = (
                ticket["journey"].id,
                ticket["cargo"],
                ticket["seat"],
            )

            if seat_key in selected_seats:
                raise serializers.ValidationError(
                    "The same seat cannot be booked twice "
                    "in one order."
                )

            selected_seats.add(seat_key)

        return tickets

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")

        order = Order.objects.create(
            user=self.context["request"].user,
        )

        Ticket.objects.bulk_create(
            [
                Ticket(
                    order=order,
                    **ticket_data,
                )
                for ticket_data in tickets_data
            ]
        )

        return order
