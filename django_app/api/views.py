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
