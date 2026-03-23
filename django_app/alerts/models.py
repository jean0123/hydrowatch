from django.conf import settings
from django.db import models

from dashboard.models import Station


class AlertRule(models.Model):
    """User-defined threshold alert for a station."""

    class Metric(models.TextChoices):
        WATER_LEVEL = "water_level", "Water Level (m)"
        FLOW_RATE = "flow_rate", "Flow Rate (m³/s)"

    class Operator(models.TextChoices):
        GT = "gt", "Greater than"
        LT = "lt", "Less than"
        GTE = "gte", "Greater than or equal"
        LTE = "lte", "Less than or equal"

    station = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="alert_rules"
    )
    metric = models.CharField(max_length=20, choices=Metric.choices)
    operator = models.CharField(max_length=4, choices=Operator.choices)
    threshold = models.FloatField()
    email = models.EmailField(help_text="Email address to notify")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_triggered = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.station.name}: {self.get_metric_display()} "
            f"{self.get_operator_display()} {self.threshold}"
        )

    def evaluate(self, value):
        """Check if the given value triggers this alert."""
        ops = {
            "gt": lambda v, t: v > t,
            "lt": lambda v, t: v < t,
            "gte": lambda v, t: v >= t,
            "lte": lambda v, t: v <= t,
        }
        return ops[self.operator](value, self.threshold)


class AlertEvent(models.Model):
    """Log of triggered alert events."""

    rule = models.ForeignKey(
        AlertRule, on_delete=models.CASCADE, related_name="events"
    )
    value = models.FloatField()
    message = models.TextField()
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Alert: {self.rule} triggered at {self.created_at}"
