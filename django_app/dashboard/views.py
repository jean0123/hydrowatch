from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from django.utils import timezone

from .csv_export import build_csv_response_content, parse_days_param
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


def station_download_csv(request, station_id):
    """Return all readings for a station (filtered by time range) as a CSV file.

    Query parameters
    ----------------
    days : int, optional
        Number of days to look back (default 7).  Accepted values mirror the
        chart selector: 1, 7, 30, 90.  Any positive integer is accepted.
    """
    station = get_object_or_404(Station, pk=station_id)
    days = parse_days_param(request.GET.get("days"))
    since = timezone.now() - timezone.timedelta(days=days)

    readings = (
        WaterLevelReading.objects.filter(station=station, timestamp__gte=since)
        .order_by("timestamp")
        .values_list("timestamp", "water_level_m", "flow_rate_cms")
    )

    csv_bytes, filename = build_csv_response_content(readings, station.station_id, days)

    response = HttpResponse(csv_bytes, content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
