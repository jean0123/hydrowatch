from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("station/<int:station_id>/", views.station_detail, name="station_detail"),
    path(
        "station/<int:station_id>/chart-data/",
        views.station_chart_data,
        name="station_chart_data",
    ),
]
