import statistics
from datetime import timedelta

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from alerts.models import AlertEvent, AlertRule
from dashboard.models import PrecipitationReading, Station, WaterLevelReading
from reports.models import Report

from .serializers import (
    AlertEventSerializer,
    AlertRuleSerializer,
    PrecipitationReadingSerializer,
    ReportSerializer,
    StationSerializer,
    WaterLevelReadingSerializer,
)

# SEN-71: stats endpoint range options (default: 7d)
_RANGE_MAP = {
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}
_DEFAULT_RANGE = "7d"


class StationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for monitoring stations."""

    queryset = Station.objects.filter(is_active=True)
    serializer_class = StationSerializer

    @action(detail=True, methods=["get"])
    def readings(self, request, pk=None):
        """Get water level readings for a specific station."""
        station = self.get_object()
        readings = WaterLevelReading.objects.filter(station=station).order_by(
            "-timestamp"
        )[:500]
        serializer = WaterLevelReadingSerializer(readings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def precipitation(self, request, pk=None):
        """Get precipitation readings for a specific station."""
        station = self.get_object()
        readings = PrecipitationReading.objects.filter(station=station).order_by(
            "-timestamp"
        )[:500]
        serializer = PrecipitationReadingSerializer(readings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        """Return min, max and mean of water level and flow rate over a time range.

        SEN-71: GET /api/stations/{id}/stats/?range=24h|7d|30d (default 7d).
        Uses the same statistical logic as reports/summarizer.py.
        """
        range_param = request.query_params.get("range", _DEFAULT_RANGE)
        delta = _RANGE_MAP.get(range_param)
        if delta is None:
            return Response(
                {
                    "error": (
                        f"Invalid range {range_param!r}. "
                        f"Valid options: {', '.join(_RANGE_MAP)}."
                    )
                },
                status=400,
            )

        station = self.get_object()
        since = timezone.now() - delta
        readings = list(
            WaterLevelReading.objects.filter(
                station=station, timestamp__gte=since
            ).order_by("timestamp")
        )

        if not readings:
            return Response(
                {
                    "station": station.pk,
                    "range": range_param,
                    "count": 0,
                    "water_level_m": None,
                    "flow_rate_cms": None,
                }
            )

        levels = [r.water_level_m for r in readings]
        flows = [r.flow_rate_cms for r in readings if r.flow_rate_cms is not None]

        water_level_stats = {
            "min": min(levels),
            "max": max(levels),
            "mean": statistics.mean(levels),
        }

        flow_rate_stats = (
            {
                "min": min(flows),
                "max": max(flows),
                "mean": statistics.mean(flows),
            }
            if flows
            else None
        )

        return Response(
            {
                "station": station.pk,
                "range": range_param,
                "count": len(readings),
                "water_level_m": water_level_stats,
                "flow_rate_cms": flow_rate_stats,
            }
        )


class WaterLevelReadingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WaterLevelReading.objects.select_related("station").all()
    serializer_class = WaterLevelReadingSerializer


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.select_related("station").all()
    serializer_class = AlertRuleSerializer


class AlertEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AlertEvent.objects.select_related("rule__station").all()
    serializer_class = AlertEventSerializer


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Report.objects.select_related("station").all()
    serializer_class = ReportSerializer
