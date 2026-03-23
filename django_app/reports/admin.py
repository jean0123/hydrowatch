from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "station", "date_from", "date_to", "created_at")
    list_filter = ("station",)
