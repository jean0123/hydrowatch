"""
test_summarizer.py
==================
Tests pytest para el módulo reports/summarizer.
Solo usa stdlib + pytest (sin dependencias de Django ni Anthropic).

Cubre el hallazgo STR-MQ7YOB57: _build_data_context debe lanzar ValueError
cuando readings está vacío, en vez de reventar con IndexError/ValueError
no controlados.
"""

import sys
import types
import importlib
import datetime

import pytest

# ---------------------------------------------------------------------------
# Stub del módulo 'anthropic' para evitar la dependencia real al importar
# el summarizer (la prueba no ejercita la llamada a la API).
# ---------------------------------------------------------------------------

def _install_anthropic_stub():
    """Inserta un stub mínimo de 'anthropic' en sys.modules si no existe."""
    if "anthropic" not in sys.modules:
        stub = types.ModuleType("anthropic")

        class _Messages:
            def create(self, **kwargs):
                raise RuntimeError("anthropic stub — not for real calls")

        class _Anthropic:
            def __init__(self, **kwargs):
                self.messages = _Messages()

        stub.Anthropic = _Anthropic
        sys.modules["anthropic"] = stub


_install_anthropic_stub()

# Ahora es seguro importar el summarizer.
from django_app.reports.summarizer import _build_data_context  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers mínimos (sin ORM de Django)
# ---------------------------------------------------------------------------

class _FakeStation:
    """Stub mínimo de Station para pasar a _build_data_context."""
    name = "Test Station"
    station_id = "TS-001"
    latitude = 19.4326
    longitude = 99.1332


class _FakeReading:
    """Stub mínimo de Reading para pasar a _build_data_context."""
    def __init__(self, water_level_m, flow_rate_cms, timestamp):
        self.water_level_m = water_level_m
        self.flow_rate_cms = flow_rate_cms
        self.timestamp = timestamp


# ---------------------------------------------------------------------------
# Casos que deben lanzar ValueError (hallazgo STR-MQ7YOB57)
# ---------------------------------------------------------------------------

class TestBuildDataContextEmptyReadings:
    """_build_data_context debe rechazar una lista vacía con ValueError."""

    def test_empty_list_raises_value_error(self):
        station = _FakeStation()
        with pytest.raises(ValueError):
            _build_data_context(station, [])

    def test_empty_list_error_message_is_informative(self):
        station = _FakeStation()
        with pytest.raises(ValueError, match="empty|vacío|readings"):
            _build_data_context(station, [])


# ---------------------------------------------------------------------------
# Caso básico correcto (smoke-test — no debe lanzar nada)
# ---------------------------------------------------------------------------

class TestBuildDataContextWithReadings:
    """_build_data_context debe funcionar con una lista no vacía."""

    def test_two_readings_returns_string(self):
        station = _FakeStation()
        readings = [
            _FakeReading(1.5, None, datetime.datetime(2024, 1, 15, 10, 0)),
            _FakeReading(1.8, None, datetime.datetime(2024, 1, 15, 11, 0)),
        ]
        result = _build_data_context(station, readings)
        assert isinstance(result, str)
        assert "Test Station" in result

    def test_multiple_readings_returns_string(self):
        station = _FakeStation()
        readings = [
            _FakeReading(1.0, 10.0, datetime.datetime(2024, 1, 15, 8, 0)),
            _FakeReading(1.5, 12.0, datetime.datetime(2024, 1, 15, 9, 0)),
            _FakeReading(1.2, 11.0, datetime.datetime(2024, 1, 15, 10, 0)),
        ]
        result = _build_data_context(station, readings)
        assert isinstance(result, str)
        assert "TS-001" in result
