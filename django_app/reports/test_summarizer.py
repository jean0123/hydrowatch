"""
test_summarizer.py
==================
Tests pytest para el módulo reports/summarizer.
Solo usa stdlib + pytest (sin dependencias de Django).

Cubre el hallazgo STR-MQ814940: _build_data_context debe lanzar ValueError
cuando readings está vacío, en lugar de reventar con IndexError/ValueError
no controlados.
"""

import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Mock 'anthropic' before importing the module under test, since anthropic
# has a native extension that may not load in all environments.
# ---------------------------------------------------------------------------
if "anthropic" not in sys.modules:
    sys.modules["anthropic"] = types.ModuleType("anthropic")

from reports.summarizer import _build_data_context  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers / stubs
# ---------------------------------------------------------------------------

class _FakeStation:
    """Stub mínimo de Station para construir el contexto."""

    def __init__(self):
        self.name = "TestStation"
        self.station_id = "TS-001"
        self.latitude = 45.1234
        self.longitude = -75.5678


class _FakeReading:
    """Stub mínimo de WaterLevelReading."""

    def __init__(self, water_level_m, flow_rate_cms=None, timestamp=None):
        self.water_level_m = water_level_m
        self.flow_rate_cms = flow_rate_cms
        if timestamp is None:
            from datetime import datetime
            self.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        else:
            self.timestamp = timestamp


# ---------------------------------------------------------------------------
# STR-MQ814940 — readings vacío debe lanzar ValueError con mensaje claro
# ---------------------------------------------------------------------------

class TestBuildDataContextEmptyReadings:
    """_build_data_context debe rechazar una lista de lecturas vacía."""

    def test_empty_readings_raises_value_error(self):
        """Con readings=[], debe lanzar ValueError (no IndexError ni similar)."""
        station = _FakeStation()
        with pytest.raises(ValueError):
            _build_data_context(station, [])

    def test_empty_readings_error_message_is_informative(self):
        """El mensaje de ValueError debe ser descriptivo."""
        station = _FakeStation()
        with pytest.raises(ValueError, match="readings"):
            _build_data_context(station, [])

    def test_empty_list_not_index_error(self):
        """Garantiza que no se propaga un IndexError (regresión)."""
        station = _FakeStation()
        try:
            _build_data_context(station, [])
            pytest.fail("Se esperaba ValueError, no se lanzó ninguna excepción")
        except ValueError:
            pass  # comportamiento correcto
        except IndexError:
            pytest.fail("Se propagó IndexError en lugar de ValueError")


# ---------------------------------------------------------------------------
# Smoke test — con lecturas válidas debe funcionar correctamente
# ---------------------------------------------------------------------------

class TestBuildDataContextWithReadings:
    """_build_data_context no debe romperse con lecturas válidas."""

    def test_two_readings_returns_string(self):
        from datetime import datetime, timedelta
        station = _FakeStation()
        base = datetime(2024, 6, 1, 8, 0, 0)
        readings = [
            _FakeReading(
                water_level_m=1.5,
                flow_rate_cms=0.8,
                timestamp=base,
            ),
            _FakeReading(
                water_level_m=1.6,
                flow_rate_cms=0.9,
                timestamp=base + timedelta(hours=1),
            ),
        ]
        result = _build_data_context(station, readings)
        assert isinstance(result, str)
        assert station.name in result

    def test_multiple_readings_returns_string_with_stats(self):
        from datetime import datetime, timedelta
        station = _FakeStation()
        base = datetime(2024, 6, 1, 0, 0, 0)
        readings = [
            _FakeReading(
                water_level_m=1.0 + i * 0.1,
                flow_rate_cms=0.5,
                timestamp=base + timedelta(hours=i),
            )
            for i in range(5)
        ]
        result = _build_data_context(station, readings)
        assert "Min" in result
        assert "Max" in result
        assert "Mean" in result
