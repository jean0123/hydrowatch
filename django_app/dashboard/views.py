from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.utils import timezone

from .models import Station, WaterLevelReading


def index(request):
    """Main dashboard view with map and station list."""
    stations = Station.objects.filter(is_active=True)
    stations_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [s.longitude, s.latitude],
                },
                "properties": {
                    "id": s.id,
                    "station_id": s.station_id,
                    "name": s.name,
                    "province": s.province,
                },
            }
            for s in stations
        ],
    }
    return render(
        request,
        "dashboard/index.html",
        {"stations": stations, "stations_geojson": stations_geojson},
    )


def station_detail(request, station_id):
    """Detail view for a single station with chart data."""
    station = get_object_or_404(Station, pk=station_id)
    return render(request, "dashboard/station_detail.html", {"station": station})


def station_chart_data(request, station_id):
    """Return JSON time-series data for Chart.js."""
    station = get_object_or_404(Station, pk=station_id)
    days = int(request.GET.get("days", 7))
    since = timezone.now() - timezone.timedelta(days=days)

    readings = (
        WaterLevelReading.objects.filter(station=station, timestamp__gte=since)
        .order_by("timestamp")
        .values_list("timestamp", "water_level_m", "flow_rate_cms")
    )

    data = {
        "station": station.name,
        "labels": [r[0].isoformat() for r in readings],
        "water_level": [r[1] for r in readings],
        "flow_rate": [r[2] for r in readings],
    }
    return JsonResponse(data)
