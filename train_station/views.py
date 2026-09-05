from django.db.models import Count
from rest_framework import mixins, viewsets
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
)

from train_station.filters import JourneyFilter
from train_station.models import (
    Crew,
    Journey,
    Order,
    Route,
    Station,
    Train,
    TrainType,
)
from train_station.serializers import (
    CrewSerializer,
    JourneyDetailSerializer,
    JourneyListSerializer,
    JourneySerializer,
    OrderSerializer,
    RouteListSerializer,
    RouteSerializer,
    StationSerializer,
    TrainListSerializer,
    TrainSerializer,
    TrainTypeSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    search_fields = ("name",)
    ordering_fields = ("name",)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []

        return [IsAdminUser()]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related(
        "source",
        "destination",
    )
    serializer_class = RouteSerializer
    filterset_fields = (
        "source",
        "destination",
    )
    ordering_fields = ("distance",)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListSerializer

        return RouteSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []

        return [IsAdminUser()]


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    search_fields = ("name",)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []

        return [IsAdminUser()]


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer
    filterset_fields = ("train_type",)
    search_fields = ("name",)
    ordering_fields = (
        "name",
        "cargo_num",
        "places_in_cargo",
    )

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TrainListSerializer

        return TrainSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []

        return [IsAdminUser()]


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    search_fields = (
        "first_name",
        "last_name",
    )
    ordering_fields = (
        "first_name",
        "last_name",
    )

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []

        return [IsAdminUser()]


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.select_related(
            "route",
            "route__source",
            "route__destination",
            "train",
            "train__train_type",
        )
        .prefetch_related(
            "crew",
            "tickets",
        )
        .annotate(
            tickets_count=Count("tickets"),
        )
    )

    filterset_class = JourneyFilter

    search_fields = (
        "route__source__name",
        "route__destination__name",
        "train__name",
    )

    ordering_fields = (
        "departure_time",
        "arrival_time",
    )

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return JourneySerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return []

        return [IsAdminUser()]


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            Order.objects.filter(
                user=self.request.user,
            )
            .prefetch_related(
                "tickets",
                "tickets__journey",
                "tickets__journey__route",
                "tickets__journey__train",
            )
        )
