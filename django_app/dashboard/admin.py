from django.contrib import admin

from .models import PrecipitationReading, Station, WaterLevelReading


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("station_id", "name", "province", "latitude", "longitude", "is_active")
    list_filter = ("province", "is_active")
    search_fields = ("station_id", "name")


@admin.register(WaterLevelReading)
class WaterLevelReadingAdmin(admin.ModelAdmin):
    list_display = ("station", "timestamp", "water_level_m", "flow_rate_cms")
    list_filter = ("station",)
    date_hierarchy = "timestamp"


@admin.register(PrecipitationReading)
class PrecipitationReadingAdmin(admin.ModelAdmin):
    list_display = ("station", "timestamp", "precipitation_mm")
    list_filter = ("station",)
    date_hierarchy = "timestamp"
