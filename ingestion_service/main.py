"""FastAPI microservice for ingesting hydrometric data from external APIs.

Fetches real-time water level data from Environment and Climate Change Canada's
Hydrometric API and stores it in the shared PostgreSQL database.
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text

from config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

# Canadian hydrometric real-time data CSV endpoint
WATEROFFICE_BASE_URL = (
    "https://dd.weather.gc.ca/hydrometric/csv"
)

# Sample BC stations for demo purposes
DEMO_STATIONS = [
    {
        "station_id": "08MH001",
        "name": "Coquitlam River near Coquitlam",
        "province": "BC",
        "latitude": 49.2833,
        "longitude": -122.7833,
    },
    {
        "station_id": "08MH005",
        "name": "Indian River near North Vancouver",
        "province": "BC",
        "latitude": 49.3667,
        "longitude": -123.0500,
    },
    {
        "station_id": "08GA010",
        "name": "Capilano River near North Vancouver",
        "province": "BC",
        "latitude": 49.3500,
        "longitude": -123.1167,
    },
    {
        "station_id": "08MH141",
        "name": "Brunette River at New Westminster",
        "province": "BC",
        "latitude": 49.2167,
        "longitude": -122.8833,
    },
    {
        "station_id": "08MF065",
        "name": "Kanaka Creek near Maple Ridge",
        "province": "BC",
        "latitude": 49.2167,
        "longitude": -122.5500,
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="HydroWatch Ingestion Service",
    description="Microservice for ingesting hydrometric data from third-party APIs",
    version="1.0.0",
    lifespan=lifespan,
)


class IngestResult(BaseModel):
    stations_upserted: int
    readings_inserted: int
    errors: list[str]


class StationResponse(BaseModel):
    station_id: str
    name: str
    province: str
    latitude: float
    longitude: float


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ingestion"}


@app.post("/ingest/stations", response_model=IngestResult)
async def ingest_stations():
    """Seed the database with demo BC hydrometric stations."""
    errors = []
    count = 0
    with engine.connect() as conn:
        for s in DEMO_STATIONS:
            try:
                conn.execute(
                    text("""
                        INSERT INTO dashboard_station
                            (station_id, name, province, latitude, longitude, is_active, created_at)
                        VALUES
                            (:station_id, :name, :province, :latitude, :longitude, true, NOW())
                        ON CONFLICT (station_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            latitude = EXCLUDED.latitude,
                            longitude = EXCLUDED.longitude
                    """),
                    s,
                )
                count += 1
            except Exception as e:
                errors.append(f"Station {s['station_id']}: {e}")
        conn.commit()

    return IngestResult(stations_upserted=count, readings_inserted=0, errors=errors)


@app.post("/ingest/readings/{station_id}", response_model=IngestResult)
async def ingest_readings(station_id: str, hours: int = 48):
    """Fetch recent water level data for a station from the Canadian Hydrometric API.

    Falls back to generating synthetic demo data if the external API is unreachable.
    """
    # Try fetching real data from Environment Canada
    province = "BC"
    url = f"{WATEROFFICE_BASE_URL}/{province}/hourly/{province}_{station_id}_hourly_hydrometric.csv"

    readings = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                readings = _parse_csv_readings(station_id, resp.text, hours)
        except httpx.RequestError:
            pass

    # Fall back to synthetic data for demo purposes
    if not readings:
        readings = _generate_demo_readings(station_id, hours)

    errors = []
    inserted = 0
    with engine.connect() as conn:
        # Lookup station PK
        row = conn.execute(
            text("SELECT id FROM dashboard_station WHERE station_id = :sid"),
            {"sid": station_id},
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Station {station_id} not found")

        station_pk = row[0]
        for r in readings:
            try:
                conn.execute(
                    text("""
                        INSERT INTO dashboard_waterlevelreading
                            (station_id, timestamp, water_level_m, flow_rate_cms, created_at)
                        VALUES
                            (:station_pk, :timestamp, :water_level, :flow_rate, NOW())
                        ON CONFLICT (station_id, timestamp) DO UPDATE SET
                            water_level_m = EXCLUDED.water_level_m,
                            flow_rate_cms = EXCLUDED.flow_rate_cms
                    """),
                    {
                        "station_pk": station_pk,
                        "timestamp": r["timestamp"],
                        "water_level": r["water_level"],
                        "flow_rate": r["flow_rate"],
                    },
                )
                inserted += 1
            except Exception as e:
                errors.append(str(e))
        conn.commit()

    return IngestResult(stations_upserted=0, readings_inserted=inserted, errors=errors)


@app.post("/ingest/all", response_model=IngestResult)
async def ingest_all():
    """Ingest stations and readings for all demo stations."""
    station_result = await ingest_stations()
    total_readings = 0
    all_errors = list(station_result.errors)

    for s in DEMO_STATIONS:
        try:
            result = await ingest_readings(s["station_id"])
            total_readings += result.readings_inserted
            all_errors.extend(result.errors)
        except Exception as e:
            all_errors.append(f"Readings for {s['station_id']}: {e}")

    return IngestResult(
        stations_upserted=station_result.stations_upserted,
        readings_inserted=total_readings,
        errors=all_errors,
    )


@app.get("/stations", response_model=list[StationResponse])
async def list_stations():
    """List available demo stations."""
    return [StationResponse(**s) for s in DEMO_STATIONS]


def _parse_csv_readings(station_id: str, csv_text: str, hours: int) -> list[dict]:
    """Parse Environment Canada CSV format into reading dicts."""
    readings = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    lines = csv_text.strip().split("\n")

    for line in lines[1:]:  # Skip header
        parts = line.split(",")
        if len(parts) < 4:
            continue
        try:
            ts = datetime.fromisoformat(parts[1].strip())
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts < cutoff:
                continue
            water_level = float(parts[2].strip()) if parts[2].strip() else None
            flow_rate = float(parts[6].strip()) if len(parts) > 6 and parts[6].strip() else None
            if water_level is not None:
                readings.append({
                    "timestamp": ts.isoformat(),
                    "water_level": water_level,
                    "flow_rate": flow_rate,
                })
        except (ValueError, IndexError):
            continue

    return readings


def _generate_demo_readings(station_id: str, hours: int) -> list[dict]:
    """Generate synthetic water level data for demonstration."""
    import math
    import hashlib

    # Use station_id as seed for deterministic but varied data
    seed = int(hashlib.md5(station_id.encode()).hexdigest()[:8], 16)
    base_level = 1.5 + (seed % 30) / 10.0  # 1.5m to 4.5m
    base_flow = 5.0 + (seed % 50) / 5.0  # 5 to 15 m³/s

    readings = []
    now = datetime.now(timezone.utc)
    for i in range(hours):
        ts = now - timedelta(hours=hours - i)
        # Sinusoidal variation + small noise
        hour_angle = (ts.hour / 24.0) * 2 * math.pi
        day_angle = (ts.day / 30.0) * 2 * math.pi
        variation = 0.3 * math.sin(hour_angle) + 0.15 * math.sin(day_angle * 3)
        noise = ((hash(f"{station_id}{i}") % 100) - 50) / 500.0

        level = base_level + variation + noise
        flow = base_flow + variation * 5 + noise * 3

        readings.append({
            "timestamp": ts.isoformat(),
            "water_level": round(level, 3),
            "flow_rate": round(max(0, flow), 3),
        })

    return readings
