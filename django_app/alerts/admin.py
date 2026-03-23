from django.contrib import admin

from .models import AlertEvent, AlertRule


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ("station", "metric", "operator", "threshold", "email", "is_active")
    list_filter = ("is_active", "metric")


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = ("rule", "value", "notified", "created_at")
    list_filter = ("notified",)
