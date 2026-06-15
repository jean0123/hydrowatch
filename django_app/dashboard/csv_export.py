"""
csv_export.py
=============
Pure-Python helpers for the CSV download feature (STR-MQFHCFGO).

This module contains ONLY stdlib code (csv, io, datetime) and carries NO
Django / GIS / ORM dependencies.  It can therefore be imported and tested in
any environment — no database, no GDAL, no Django settings required.

Public API
----------
build_csv_response_content(readings, station_id, days)
    Serialise an iterable of (timestamp, water_level_m, flow_rate_cms) tuples
    into a CSV byte-string and return (csv_bytes, filename).

parse_days_param(raw)
    Safely convert a raw query-parameter value to a positive integer.
    Falls back to 7 on any error or invalid input.
"""

import csv
import io
from datetime import timedelta as _timedelta

# ---------------------------------------------------------------------------
# Public constants
# ---------------------------------------------------------------------------

DEFAULT_DAYS: int = 7
"""Default time-range in days when the query parameter is absent or invalid."""


# ---------------------------------------------------------------------------
# parse_days_param
# ---------------------------------------------------------------------------

def parse_days_param(raw) -> int:
    """Convert *raw* (a GET query parameter value) to a positive integer.

    Parameters
    ----------
    raw : str | None | Any
        The raw value from ``request.GET.get('days')``.

    Returns
    -------
    int
        A positive integer number of days.  Defaults to :data:`DEFAULT_DAYS`
        when *raw* is ``None``, non-numeric, zero, or negative.

    Notes
    -----
    This function never raises — all errors are silently swallowed and the
    default is returned instead.
    """
    if raw is None:
        return DEFAULT_DAYS
    try:
        days = int(raw)
    except (ValueError, TypeError):
        return DEFAULT_DAYS
    if days < 1:
        return DEFAULT_DAYS
    return days


# ---------------------------------------------------------------------------
# build_csv_response_content
# ---------------------------------------------------------------------------

def build_csv_response_content(readings, station_id: str, days: int):
    """Serialise reading tuples to CSV bytes and produce a safe filename.

    Parameters
    ----------
    readings : iterable of (timestamp, water_level_m, flow_rate_cms)
        Iterable of 3-tuples as returned by
        ``WaterLevelReading.objects.values_list('timestamp', 'water_level_m',
        'flow_rate_cms')``.  ``timestamp`` must have an ``.isoformat()``
        method; ``flow_rate_cms`` may be ``None``.
    station_id : str
        The ``station_id`` string of the station (used in the filename).
    days : int
        Number of days covered by the export (used in the filename).

    Returns
    -------
    (csv_bytes: bytes, filename: str)
        ``csv_bytes`` is UTF-8 encoded CSV content with a header row.
        ``filename`` is a safe ASCII filename such as
        ``readings_05AA001_7d.csv``.
    """
    # Build a safe filename — strip anything that isn't alphanumeric, hyphen
    # or underscore to prevent path-traversal issues.
    safe_sid = "".join(c for c in station_id if c.isalnum() or c in "-_")
    filename = f"readings_{safe_sid}_{days}d.csv"

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["timestamp", "water_level_m", "flow_rate_cms"])

    for timestamp, water_level_m, flow_rate_cms in readings:
        writer.writerow([
            timestamp.isoformat(),
            water_level_m,
            "" if flow_rate_cms is None else flow_rate_cms,
        ])

    return buf.getvalue().encode("utf-8"), filename
