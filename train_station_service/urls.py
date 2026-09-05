from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),
    path(
        "api/train-station/",
        include("train_station.urls"),
    ),
    path(
        "api/user/",
        include("user.urls"),
    ),
]
