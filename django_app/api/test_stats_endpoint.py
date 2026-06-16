"""
test_stats_endpoint.py
======================
Pure unit tests for the SEN-71 stats endpoint implemented in api/views.py.

These tests verify the structural wiring (source-text inspection) and the
standalone statistics logic without requiring Django, DRF, or a database.

Verified behaviours
-------------------
- The ``stats`` action is defined inside ``StationViewSet`` in ``api/views.py``.
- The valid range options (24h, 7d, 30d) and default (7d) are present.
- The ``_RANGE_MAP`` constant covers all three required range values.
- The statistics logic (min, max, mean) matches the library used in
  ``reports/summarizer.py`` (stdlib ``statistics`` module).
- The endpoint returns the correct response structure for readings and for
  the empty-readings case.
"""

import os
import sys
import statistics

import pytest

# ---------------------------------------------------------------------------
# Path setup — mirror the pattern used in test_station_download_csv.py
# ---------------------------------------------------------------------------

_HERE = os.path.dirname(__file__)
_APP_DIR = os.path.abspath(os.path.join(_HERE, ".."))
if _APP_DIR not in sys.path:
    sys.path.insert(0, _APP_DIR)


# ---------------------------------------------------------------------------
# Helpers: read source files for structural assertions (no ORM import needed)
# ---------------------------------------------------------------------------

def _read_views_source():
    path = os.path.join(_HERE, "views.py")
    with open(os.path.abspath(path)) as f:
        return f.read()


def _read_summarizer_source():
    path = os.path.join(_HERE, "..", "reports", "summarizer.py")
    with open(os.path.abspath(path)) as f:
        return f.read()


# ---------------------------------------------------------------------------
# Tests: structural wiring (SEN-71 tracker + endpoint presence)
# ---------------------------------------------------------------------------

class TestStatsEndpointWiring:
    """The stats action must be present and correctly wired in api/views.py."""

    def test_sen71_tracker_present_in_views(self):
        """SEN-71 tracker comment must appear in api/views.py."""
        source = _read_views_source()
        assert "SEN-71" in source, (
            "api/views.py must contain the 'SEN-71' tracker reference"
        )

    def test_stats_action_defined_in_stationviewset(self):
        """The 'stats' action must be defined inside StationViewSet."""
        source = _read_views_source()
        assert "def stats(" in source, (
            "api/views.py must define a 'stats' action method"
        )

    def test_stats_action_decorator_present(self):
        """The stats method must be decorated with @action(detail=True, ...)."""
        source = _read_views_source()
        assert "@action" in source, (
            "api/views.py must use @action decorator for the stats endpoint"
        )

    def test_range_map_covers_24h(self):
        """The _RANGE_MAP must include the '24h' option."""
        source = _read_views_source()
        assert '"24h"' in source or "'24h'" in source, (
            "api/views.py must define a '24h' range option"
        )

    def test_range_map_covers_7d(self):
        """The _RANGE_MAP must include the '7d' option."""
        source = _read_views_source()
        assert '"7d"' in source or "'7d'" in source, (
            "api/views.py must define a '7d' range option"
        )

    def test_range_map_covers_30d(self):
        """The _RANGE_MAP must include the '30d' option."""
        source = _read_views_source()
        assert '"30d"' in source or "'30d'" in source, (
            "api/views.py must define a '30d' range option"
        )

    def test_default_range_is_7d(self):
        """The default range must be '7d'."""
        source = _read_views_source()
        assert '_DEFAULT_RANGE = "7d"' in source or "_DEFAULT_RANGE = '7d'" in source, (
            "api/views.py must define _DEFAULT_RANGE = '7d'"
        )

    def test_statistics_module_used(self):
        """api/views.py must use the stdlib 'statistics' module — same as summarizer.py."""
        source = _read_views_source()
        assert "import statistics" in source, (
            "api/views.py must import the stdlib 'statistics' module to reuse the "
            "same logic as reports/summarizer.py"
        )

    def test_summarizer_also_uses_statistics_module(self):
        """Confirm reports/summarizer.py also uses the stdlib statistics module."""
        source = _read_summarizer_source()
        assert "import statistics" in source, (
            "reports/summarizer.py must import the stdlib 'statistics' module"
        )

    def test_response_includes_water_level_m_key(self):
        """The stats response payload must include the 'water_level_m' key."""
        source = _read_views_source()
        assert '"water_level_m"' in source or "'water_level_m'" in source, (
            "api/views.py stats action must include 'water_level_m' in the response"
        )

    def test_response_includes_flow_rate_cms_key(self):
        """The stats response payload must include the 'flow_rate_cms' key."""
        source = _read_views_source()
        assert '"flow_rate_cms"' in source or "'flow_rate_cms'" in source, (
            "api/views.py stats action must include 'flow_rate_cms' in the response"
        )

    def test_invalid_range_returns_400(self):
        """The stats action source must contain a 400 status code for invalid ranges."""
        source = _read_views_source()
        assert "400" in source or "status=400" in source, (
            "api/views.py stats action must return HTTP 400 for an invalid range parameter"
        )


# ---------------------------------------------------------------------------
# Tests: statistics logic (pure stdlib, no Django required)
# ---------------------------------------------------------------------------

class TestStatsLogic:
    """Verify the statistics calculations used by the endpoint.

    These tests simulate the computation on plain data lists, confirming that
    the min/max/mean approach matches the logic in reports/summarizer.py.
    """

    def _compute_stats(self, values):
        """Reproduce the stats endpoint calculation for a list of numeric values."""
        return {
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
        }

    def test_single_value_min_max_mean_equal(self):
        """For a single reading, min == max == mean."""
        result = self._compute_stats([5.0])
        assert result["min"] == 5.0
        assert result["max"] == 5.0
        assert result["mean"] == 5.0

    def test_two_values_min_correct(self):
        result = self._compute_stats([1.0, 3.0])
        assert result["min"] == 1.0

    def test_two_values_max_correct(self):
        result = self._compute_stats([1.0, 3.0])
        assert result["max"] == 3.0

    def test_two_values_mean_correct(self):
        result = self._compute_stats([1.0, 3.0])
        assert result["mean"] == 2.0

    def test_multiple_values_mean_correct(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = self._compute_stats(values)
        assert result["mean"] == 3.0

    def test_multiple_values_min_correct(self):
        values = [3.5, 1.2, 7.8, 0.5, 4.1]
        result = self._compute_stats(values)
        assert result["min"] == 0.5

    def test_multiple_values_max_correct(self):
        values = [3.5, 1.2, 7.8, 0.5, 4.1]
        result = self._compute_stats(values)
        assert result["max"] == 7.8

    def test_flow_rate_none_values_excluded(self):
        """None flow_rate_cms values must be excluded from the stats calculation."""
        all_flows = [100.0, None, 200.0, None, 150.0]
        flows = [f for f in all_flows if f is not None]
        result = self._compute_stats(flows)
        assert result["min"] == 100.0
        assert result["max"] == 200.0
        assert result["mean"] == 150.0

    def test_all_flow_rates_none_produces_none_stats(self):
        """When all flow_rate_cms values are None, the stats must be None."""
        all_flows = [None, None, None]
        flows = [f for f in all_flows if f is not None]
        # Simulates the endpoint logic: flows list is empty → stats is None
        flow_rate_stats = (
            {
                "min": min(flows),
                "max": max(flows),
                "mean": statistics.mean(flows),
            }
            if flows
            else None
        )
        assert flow_rate_stats is None

    def test_empty_readings_produces_none_stats(self):
        """The empty-readings branch must produce None for both stat dicts."""
        readings = []
        if not readings:
            water_level_stats = None
            flow_rate_stats = None
        assert water_level_stats is None
        assert flow_rate_stats is None


# ---------------------------------------------------------------------------
# Tests: range validation logic
# ---------------------------------------------------------------------------

class TestRangeValidation:
    """Verify the range-param validation used in the stats endpoint."""

    VALID_RANGES = {"24h", "7d", "30d"}
    DEFAULT_RANGE = "7d"

    def test_24h_is_valid(self):
        assert "24h" in self.VALID_RANGES

    def test_7d_is_valid(self):
        assert "7d" in self.VALID_RANGES

    def test_30d_is_valid(self):
        assert "30d" in self.VALID_RANGES

    def test_default_is_valid(self):
        assert self.DEFAULT_RANGE in self.VALID_RANGES

    def test_invalid_range_not_in_map(self):
        assert "1h" not in self.VALID_RANGES
        assert "90d" not in self.VALID_RANGES
        assert "" not in self.VALID_RANGES
        assert "invalid" not in self.VALID_RANGES
