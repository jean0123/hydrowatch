"""
test_station_download_csv.py
============================
Pure unit tests for the CSV-download helpers introduced in STR-MQFHCFGO.

These tests exercise ``dashboard.csv_export`` which contains only stdlib code
(csv, io, datetime) and carries NO Django / GIS / ORM dependencies.  The
module can therefore be imported and run in any Python environment — no
database, no GDAL, no Django settings required.

Verified behaviours
-------------------
``parse_days_param``
  - Returns DEFAULT_DAYS (7) when input is None, empty, non-numeric, or ≤ 0.
  - Returns the integer value when input is a valid positive int or numeric str.

``build_csv_response_content``
  - Returns (bytes, str) where bytes is UTF-8 CSV and str is the filename.
  - CSV header row is exactly ``timestamp,water_level_m,flow_rate_cms``.
  - A NULL (None) ``flow_rate_cms`` appears as an empty cell, NOT "None".
  - Timestamps are written as ISO-8601 strings (contain 'T').
  - Non-zero readings produce the correct number of data rows.
  - The filename contains the station_id and the number of days.
  - Characters unsafe for filenames are stripped from station_id.
"""

import csv
import io
import sys
import os
from datetime import datetime, timedelta, timezone as dt_timezone

import pytest

# ---------------------------------------------------------------------------
# Path setup — mirror the pattern used in test_range_validators.py
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(__file__)
_APP_DIR = os.path.abspath(os.path.join(_HERE, ".."))
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)

from dashboard.csv_export import build_csv_response_content, parse_days_param, DEFAULT_DAYS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ts(offset_days=0):
    """Return a timezone-aware UTC datetime offset by *offset_days* from now."""
    return datetime(2024, 6, 15, 12, 0, 0, tzinfo=dt_timezone.utc) - timedelta(days=offset_days)


def _parse(csv_bytes: bytes):
    """Parse UTF-8 CSV bytes into (header_row, data_rows)."""
    text = csv_bytes.decode("utf-8")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return [], []
    return rows[0], rows[1:]


# ---------------------------------------------------------------------------
# Tests: parse_days_param
# ---------------------------------------------------------------------------

class TestParseDaysParam:
    """parse_days_param must return a safe positive integer in all cases."""

    def test_none_returns_default(self):
        """None (missing query param) → DEFAULT_DAYS."""
        assert parse_days_param(None) == DEFAULT_DAYS

    def test_empty_string_returns_default(self):
        assert parse_days_param("") == DEFAULT_DAYS

    def test_zero_returns_default(self):
        assert parse_days_param("0") == DEFAULT_DAYS

    def test_negative_returns_default(self):
        assert parse_days_param("-5") == DEFAULT_DAYS

    def test_non_numeric_string_returns_default(self):
        assert parse_days_param("abc") == DEFAULT_DAYS

    def test_float_string_returns_default(self):
        """'3.5' cannot be int()-converted directly → falls back."""
        assert parse_days_param("3.5") == DEFAULT_DAYS

    def test_valid_1_returns_1(self):
        assert parse_days_param("1") == 1

    def test_valid_7_returns_7(self):
        assert parse_days_param("7") == 7

    def test_valid_30_returns_30(self):
        assert parse_days_param("30") == 30

    def test_valid_90_returns_90(self):
        assert parse_days_param("90") == 90

    def test_integer_input_accepted(self):
        """Direct integer input (not a string) should also work."""
        assert parse_days_param(14) == 14

    def test_large_positive_accepted(self):
        assert parse_days_param("365") == 365

    def test_default_days_is_7(self):
        """Sanity check: the module constant must equal 7."""
        assert DEFAULT_DAYS == 7


# ---------------------------------------------------------------------------
# Tests: build_csv_response_content — structure
# ---------------------------------------------------------------------------

class TestBuildCsvResponseStructure:
    """Return type, header row, and filename structure."""

    def test_returns_tuple_of_bytes_and_str(self):
        result = build_csv_response_content([], "05AA001", 7)
        assert isinstance(result, tuple)
        assert len(result) == 2
        csv_bytes, filename = result
        assert isinstance(csv_bytes, bytes)
        assert isinstance(filename, str)

    def test_csv_bytes_are_utf8_decodable(self):
        csv_bytes, _ = build_csv_response_content([], "05AA001", 7)
        csv_bytes.decode("utf-8")  # must not raise

    def test_header_row_is_correct(self):
        csv_bytes, _ = build_csv_response_content([], "05AA001", 7)
        header, _ = _parse(csv_bytes)
        assert header == ["timestamp", "water_level_m", "flow_rate_cms"]

    def test_empty_readings_only_header(self):
        csv_bytes, _ = build_csv_response_content([], "05AA001", 7)
        _, data = _parse(csv_bytes)
        assert data == []

    def test_filename_contains_station_id(self):
        _, filename = build_csv_response_content([], "05AA001", 7)
        assert "05AA001" in filename

    def test_filename_contains_days(self):
        _, filename = build_csv_response_content([], "05AA001", 30)
        assert "30" in filename

    def test_filename_ends_with_csv(self):
        _, filename = build_csv_response_content([], "05AA001", 7)
        assert filename.endswith(".csv")

    def test_filename_strips_path_traversal_chars(self):
        """Slashes and dots in station_id must be stripped from the filename."""
        _, filename = build_csv_response_content([], "../evil/path", 7)
        assert "/" not in filename
        assert ".." not in filename


# ---------------------------------------------------------------------------
# Tests: build_csv_response_content — data rows
# ---------------------------------------------------------------------------

class TestBuildCsvResponseData:
    """Correctness of CSV data rows."""

    def test_one_reading_one_data_row(self):
        readings = [(_ts(1), 1.5, 100.0)]
        csv_bytes, _ = build_csv_response_content(readings, "01AA001", 7)
        _, data = _parse(csv_bytes)
        assert len(data) == 1

    def test_three_readings_three_data_rows(self):
        readings = [
            (_ts(1), 1.5, 100.0),
            (_ts(2), 2.3, None),
            (_ts(3), 0.8, 55.5),
        ]
        csv_bytes, _ = build_csv_response_content(readings, "01AA001", 7)
        _, data = _parse(csv_bytes)
        assert len(data) == 3

    def test_water_level_value_correct(self):
        readings = [(_ts(1), 3.75, 42.0)]
        csv_bytes, _ = build_csv_response_content(readings, "01AA001", 7)
        _, data = _parse(csv_bytes)
        assert data[0][1] == "3.75"

    def test_flow_rate_value_correct(self):
        readings = [(_ts(1), 1.0, 99.5)]
        csv_bytes, _ = build_csv_response_content(readings, "01AA001", 7)
        _, data = _parse(csv_bytes)
        assert data[0][2] == "99.5"

    def test_null_flow_rate_produces_empty_cell_not_none_string(self):
        """This is the key correctness check: NULL flow_rate_cms must appear
        as an empty CSV cell — NOT the string 'None' — so Excel imports work."""
        readings = [(_ts(1), 2.3, None)]
        csv_bytes, _ = build_csv_response_content(readings, "01AA001", 7)
        _, data = _parse(csv_bytes)
        assert len(data) == 1
        assert data[0][2] == ""         # empty cell ✓
        assert data[0][2] != "None"     # NOT the string "None"

    def test_timestamp_is_iso8601(self):
        """Timestamps must contain the 'T' separator required by ISO-8601."""
        ts = _ts(1)
        readings = [(ts, 1.0, 1.0)]
        csv_bytes, _ = build_csv_response_content(readings, "01AA001", 7)
        _, data = _parse(csv_bytes)
        assert "T" in data[0][0]

    def test_timestamp_matches_input(self):
        """The exact isoformat string of the input timestamp must appear."""
        ts = _ts(1)
        readings = [(ts, 1.0, 1.0)]
        csv_bytes, _ = build_csv_response_content(readings, "01AA001", 7)
        _, data = _parse(csv_bytes)
        assert data[0][0] == ts.isoformat()

    def test_multiple_values_correct(self):
        """Water level values of all rows round-trip correctly."""
        readings = [
            (_ts(1), 1.5, 100.0),
            (_ts(2), 2.3, None),
            (_ts(3), 0.8, 55.5),
        ]
        csv_bytes, _ = build_csv_response_content(readings, "01AA001", 7)
        _, data = _parse(csv_bytes)
        water_levels = sorted(float(r[1]) for r in data)
        assert water_levels == [0.8, 1.5, 2.3]


# ---------------------------------------------------------------------------
# Tests: URL registration (inspect urls.py source, no GIS import needed)
# ---------------------------------------------------------------------------

class TestUrlRegistration:
    """The URL pattern for station_download_csv must be present in urls.py."""

    def test_download_csv_pattern_in_urlconf_source(self):
        """The urls.py file must contain the 'station_download_csv' name.
        We check the source text to avoid importing the module (which would
        chain-import models.py → GIS → GDAL which is absent in the test env).
        """
        urls_path = os.path.join(_HERE, "..", "dashboard", "urls.py")
        with open(os.path.abspath(urls_path)) as f:
            source = f.read()
        assert "station_download_csv" in source, (
            "dashboard/urls.py must contain a URL named 'station_download_csv'"
        )

    def test_download_csv_path_in_urlconf_source(self):
        """The url path 'download-csv/' must be present in urls.py."""
        urls_path = os.path.join(_HERE, "..", "dashboard", "urls.py")
        with open(os.path.abspath(urls_path)) as f:
            source = f.read()
        assert "download-csv" in source, (
            "dashboard/urls.py must contain the path 'download-csv/'"
        )

    def test_download_csv_view_referenced_in_views_source(self):
        """views.py must define 'station_download_csv'."""
        views_path = os.path.join(_HERE, "..", "dashboard", "views.py")
        with open(os.path.abspath(views_path)) as f:
            source = f.read()
        assert "def station_download_csv" in source, (
            "dashboard/views.py must define station_download_csv()"
        )

    def test_csv_export_module_imported_in_views_source(self):
        """views.py must import from csv_export (the pure helper module)."""
        views_path = os.path.join(_HERE, "..", "dashboard", "views.py")
        with open(os.path.abspath(views_path)) as f:
            source = f.read()
        assert "csv_export" in source, (
            "dashboard/views.py must import from dashboard.csv_export"
        )

    def test_download_csv_button_in_template(self):
        """The station_detail template must contain a Download CSV link."""
        tmpl_path = os.path.join(
            _HERE, "..", "dashboard", "templates", "dashboard", "station_detail.html"
        )
        with open(os.path.abspath(tmpl_path)) as f:
            source = f.read()
        assert "download-csv" in source.lower() or "Download CSV" in source, (
            "station_detail.html must contain a Download CSV link"
        )
