"""Tests for reports/summarizer.py — focused on _build_data_context.

STR-MQ7XVO9V: _build_data_context must raise ValueError when readings is empty.
"""

import sys
import types
import pytest
from unittest.mock import MagicMock
from datetime import datetime


# ---------------------------------------------------------------------------
# Stub out the `anthropic` dependency so the module can be imported without
# the real package being available in this test environment.
# ---------------------------------------------------------------------------

def _stub_anthropic():
    """Insert a minimal fake anthropic module into sys.modules if needed."""
    if "anthropic" not in sys.modules:
        fake = types.ModuleType("anthropic")
        fake.Anthropic = MagicMock()
        sys.modules["anthropic"] = fake


_stub_anthropic()

from django_app.reports.summarizer import _build_data_context  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_station(name="Test Station", station_id="TS001", latitude=1.0, longitude=2.0):
    station = MagicMock()
    station.name = name
    station.station_id = station_id
    station.latitude = latitude
    station.longitude = longitude
    return station


def _make_reading(water_level_m, timestamp_str, flow_rate_cms=None):
    reading = MagicMock()
    reading.water_level_m = water_level_m
    reading.timestamp = datetime.fromisoformat(timestamp_str)
    reading.flow_rate_cms = flow_rate_cms
    return reading


# ---------------------------------------------------------------------------
# Tests: empty readings must raise ValueError (STR-MQ7XVO9V)
# ---------------------------------------------------------------------------

class TestBuildDataContextEmptyReadings:
    """_build_data_context must raise ValueError when readings is empty."""

    def test_empty_list_raises_value_error(self):
        """Core regression test: empty list must raise ValueError, not IndexError."""
        station = _make_station()
        with pytest.raises(ValueError, match="readings must not be empty"):
            _build_data_context(station, [])

    def test_empty_list_raises_value_error_not_index_error(self):
        """Before the fix, readings[0] / readings[-1] raised IndexError."""
        station = _make_station()
        with pytest.raises(ValueError):
            _build_data_context(station, [])

    def test_error_message_is_informative(self):
        """The ValueError message should mention that readings is empty."""
        station = _make_station()
        with pytest.raises(ValueError) as exc_info:
            _build_data_context(station, [])
        assert "empty" in str(exc_info.value).lower() or "readings" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Tests: non-empty readings still work correctly
# ---------------------------------------------------------------------------

class TestBuildDataContextNonEmpty:
    """Sanity-check that _build_data_context still works with valid readings."""

    def test_two_readings_returns_string(self):
        station = _make_station()
        r1 = _make_reading(1.5, "2024-01-01T00:00:00")
        r2 = _make_reading(1.7, "2024-01-01T01:00:00")
        result = _build_data_context(station, [r1, r2])
        assert isinstance(result, str)
        assert "Test Station" in result

    def test_context_contains_water_level_section(self):
        station = _make_station()
        r1 = _make_reading(2.0, "2024-03-01T08:00:00")
        r2 = _make_reading(2.5, "2024-03-01T09:00:00")
        result = _build_data_context(station, [r1, r2])
        assert "Water Level" in result

    def test_context_includes_flow_rate_when_present(self):
        station = _make_station(name="River Alpha")
        r1 = _make_reading(2.0, "2024-03-01T08:00:00", flow_rate_cms=10.0)
        r2 = _make_reading(2.5, "2024-03-01T09:00:00", flow_rate_cms=12.0)
        result = _build_data_context(station, [r1, r2])
        assert "Flow Rate" in result
