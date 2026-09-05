import django_filters

from train_station.models import Journey


class JourneyFilter(django_filters.FilterSet):
    source = django_filters.CharFilter(
        field_name="route__source__name",
        lookup_expr="icontains",
    )
    destination = django_filters.CharFilter(
        field_name="route__destination__name",
        lookup_expr="icontains",
    )
    date = django_filters.DateFilter(
        field_name="departure_time",
        lookup_expr="date",
    )
    train = django_filters.CharFilter(
        field_name="train__name",
        lookup_expr="icontains",
    )

    class Meta:
        model = Journey
        fields = (
            "source",
            "destination",
            "date",
            "train",
        )
