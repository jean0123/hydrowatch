"""Celery tasks for scheduled data ingestion and alert evaluation."""

import logging

import requests
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def ingest_all_stations(self):
    """Trigger the ingestion service to fetch data for all stations.

    Scheduled to run every hour via Celery Beat.
    """
    try:
        url = f"{settings.INGESTION_SERVICE_URL}/ingest/all"
        resp = requests.post(url, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        logger.info(
            "Ingestion complete: %d stations, %d readings, %d errors",
            result["stations_upserted"],
            result["readings_inserted"],
            len(result["errors"]),
        )
        return result
    except requests.RequestException as exc:
        logger.error("Ingestion failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)


@shared_task
def evaluate_alerts():
    """Check all active alert rules against the latest readings.

    Runs after each ingestion cycle.
    """
    from alerts.models import AlertEvent, AlertRule
    from dashboard.models import WaterLevelReading

    rules = AlertRule.objects.filter(is_active=True).select_related("station")
    triggered = 0

    for rule in rules:
        latest = (
            WaterLevelReading.objects.filter(station=rule.station)
            .order_by("-timestamp")
            .first()
        )
        if not latest:
            continue

        value = (
            latest.water_level_m
            if rule.metric == "water_level"
            else latest.flow_rate_cms
        )
        if value is None:
            continue

        if rule.evaluate(value):
            # Cooldown: don't re-trigger within 1 hour
            if rule.last_triggered and (
                timezone.now() - rule.last_triggered
            ).total_seconds() < 3600:
                continue

            message = (
                f"Alert: {rule.station.name} - "
                f"{rule.get_metric_display()} is {value:.2f}, "
                f"which is {rule.get_operator_display()} {rule.threshold}"
            )

            event = AlertEvent.objects.create(
                rule=rule, value=value, message=message
            )

            # Send email notification
            try:
                send_mail(
                    subject=f"[HydroWatch] Alert: {rule.station.name}",
                    message=message,
                    from_email="alerts@hydrowatch.local",
                    recipient_list=[rule.email],
                    fail_silently=True,
                )
                event.notified = True
                event.save(update_fields=["notified"])
            except Exception as exc:
                logger.warning("Failed to send alert email: %s", exc)

            rule.last_triggered = timezone.now()
            rule.save(update_fields=["last_triggered"])
            triggered += 1

    logger.info("Alert evaluation complete: %d alerts triggered", triggered)
    return {"triggered": triggered}


@shared_task
def ingest_and_evaluate():
    """Chain: ingest data then evaluate alerts."""
    ingest_all_stations.apply_async(
        link=evaluate_alerts.si()
    )
