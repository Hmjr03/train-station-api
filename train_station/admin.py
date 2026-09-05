from django.contrib import admin

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


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "latitude",
        "longitude",
    )
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source",
        "destination",
        "distance",
    )
    list_filter = (
        "source",
        "destination",
    )


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "cargo_num",
        "places_in_cargo",
        "train_type",
    )
    list_filter = ("train_type",)
    search_fields = ("name",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
    )
    search_fields = (
        "first_name",
        "last_name",
    )


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "route",
        "train",
        "departure_time",
        "arrival_time",
    )
    list_filter = (
        "train",
        "route",
    )
    filter_horizontal = ("crew",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
    )
    list_filter = ("created_at",)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "journey",
        "cargo",
        "seat",
        "order",
    )
    list_filter = ("journey",)
