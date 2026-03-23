from django.contrib.gis.db import models as gis_models
from django.db import models


class Station(models.Model):
    """A hydrometric monitoring station."""

    station_id = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    province = models.CharField(max_length=64, blank=True, default="")
    location = gis_models.PointField(geography=True, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.station_id})"


class WaterLevelReading(models.Model):
    """A single water level reading from a station."""

    station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="readings"
    )
    timestamp = models.DateTimeField(db_index=True)
    water_level_m = models.FloatField(help_text="Water level in metres")
    flow_rate_cms = models.FloatField(
        null=True, blank=True, help_text="Flow rate in cubic metres per second"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        unique_together = ["station", "timestamp"]
        indexes = [
            models.Index(fields=["station", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.station.station_id} @ {self.timestamp}: {self.water_level_m}m"


class PrecipitationReading(models.Model):
    """Precipitation data for a station."""

    station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="precipitation"
    )
    timestamp = models.DateTimeField(db_index=True)
    precipitation_mm = models.FloatField(help_text="Precipitation in millimetres")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        unique_together = ["station", "timestamp"]

    def __str__(self):
        return f"{self.station.station_id} @ {self.timestamp}: {self.precipitation_mm}mm"
