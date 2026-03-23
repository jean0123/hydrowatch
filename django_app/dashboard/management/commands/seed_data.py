"""Django management command to seed the database with demo data."""

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed the database with demo stations and readings via the ingestion service"

    def handle(self, *args, **options):
        url = f"{settings.INGESTION_SERVICE_URL}/ingest/all"
        self.stdout.write(f"Calling ingestion service at {url}...")

        try:
            resp = requests.post(url, timeout=120)
            resp.raise_for_status()
            result = resp.json()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {result['stations_upserted']} stations "
                    f"and {result['readings_inserted']} readings."
                )
            )
            if result["errors"]:
                for err in result["errors"]:
                    self.stdout.write(self.style.WARNING(f"  Warning: {err}"))
        except requests.RequestException as exc:
            self.stdout.write(self.style.ERROR(f"Failed: {exc}"))
