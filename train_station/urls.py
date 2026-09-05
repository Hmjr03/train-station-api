from django.urls import include, path
from rest_framework.routers import DefaultRouter

from train_station.views import (
    CrewViewSet,
    JourneyViewSet,
    OrderViewSet,
    RouteViewSet,
    StationViewSet,
    TrainTypeViewSet,
    TrainViewSet,
)


app_name = "train_station"


router = DefaultRouter()

router.register(
    "stations",
    StationViewSet,
    basename="station",
)
router.register(
    "routes",
    RouteViewSet,
    basename="route",
)
router.register(
    "train-types",
    TrainTypeViewSet,
    basename="train-type",
)
router.register(
    "trains",
    TrainViewSet,
    basename="train",
)
router.register(
    "crews",
    CrewViewSet,
    basename="crew",
)
router.register(
    "journeys",
    JourneyViewSet,
    basename="journey",
)
router.register(
    "orders",
    OrderViewSet,
    basename="order",
)


urlpatterns = [
    path("", include(router.urls)),
]
