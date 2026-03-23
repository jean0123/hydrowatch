from rest_framework import serializers

from alerts.models import AlertEvent, AlertRule
from dashboard.models import PrecipitationReading, Station, WaterLevelReading
from reports.models import Report


class StationSerializer(serializers.ModelSerializer):
    reading_count = serializers.SerializerMethodField()

    class Meta:
        model = Station
        fields = [
            "id", "station_id", "name", "province",
            "latitude", "longitude", "is_active", "reading_count",
        ]

    def get_reading_count(self, obj):
        return obj.readings.count()


class WaterLevelReadingSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = WaterLevelReading
        fields = [
            "id", "station", "station_name", "timestamp",
            "water_level_m", "flow_rate_cms",
        ]


class PrecipitationReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecipitationReading
        fields = ["id", "station", "timestamp", "precipitation_mm"]


class AlertRuleSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = AlertRule
        fields = [
            "id", "station", "station_name", "metric", "operator",
            "threshold", "email", "is_active", "last_triggered",
        ]


class AlertEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertEvent
        fields = ["id", "rule", "value", "message", "notified", "created_at"]


class ReportSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source="station.name", read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = [
            "id", "station", "station_name", "title",
            "ai_summary", "date_from", "date_to", "download_url", "created_at",
        ]

    def get_download_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None
