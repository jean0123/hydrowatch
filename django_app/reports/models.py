from django.db import models

from dashboard.models import Station


class Report(models.Model):
    """Generated PDF report for a station."""

    station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="reports"
    )
    title = models.CharField(max_length=255)
    ai_summary = models.TextField(blank=True, default="")
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    pdf_file = models.FileField(upload_to="reports/%Y/%m/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.created_at:%Y-%m-%d})"
