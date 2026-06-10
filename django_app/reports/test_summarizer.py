"""
test_summarizer.py
==================
Tests pytest para el módulo summarizer de reports.

Cubre el hallazgo STR-MQ7XCBI1: _build_data_context debe lanzar
ValueError cuando readings está vacío, en lugar de reventar con
IndexError / StatisticsError no controlados.
"""

import pytest

# Import the private helper directly so we can test it in isolation.
from django_app.reports.summarizer import _build_data_context


# ---------------------------------------------------------------------------
# Minimal stubs — no Django models needed for unit-testing the helper.
# ---------------------------------------------------------------------------

class _StubStation:
    """Minimal station-like object for testing."""
    name = "Test Station"
    station_id = "TST001"
    latitude = 45.0
    longitude = -75.0


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestBuildDataContextEmptyReadings:
    """_build_data_context must raise ValueError for empty readings."""

    def test_empty_list_raises_value_error(self):
        """Core requirement of STR-MQ7XCBI1.

        Without the fix this call raises IndexError (readings[0] / readings[-1])
        or StatisticsError from statistics.stdev([]).  With the fix it must
        raise ValueError with a descriptive message before any list access.
        """
        station = _StubStation()
        with pytest.raises(ValueError):
            _build_data_context(station, [])

    def test_empty_list_error_message_mentions_readings(self):
        """The error message should be informative."""
        station = _StubStation()
        with pytest.raises(ValueError, match=r"(?i)reading|empty|vacío"):
            _build_data_context(station, [])

    def test_empty_list_not_index_error(self):
        """The exception type must be ValueError, not IndexError."""
        station = _StubStation()
        try:
            _build_data_context(station, [])
            pytest.fail("Expected ValueError was not raised")
        except ValueError:
            pass  # Correct behaviour
        except (IndexError, Exception) as exc:
            pytest.fail(
                f"Expected ValueError but got {type(exc).__name__}: {exc}"
            )
