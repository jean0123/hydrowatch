"""Tests for ingestion_service/coordinate_validators.py (SEN-49).

Covers:
- Exact boundary values ±90 (latitude) and ±180 (longitude) must be VALID.
- Values strictly outside those boundaries must be INVALID.
- Mixed batches: invalid readings are rejected with a clear error message
  (containing station_id and the bad value) without preventing valid readings
  from being processed.
"""

import pytest

from ingestion_service.coordinate_validators import validate_coordinates


# ---------------------------------------------------------------------------
# Valid boundary values — must NOT raise
# ---------------------------------------------------------------------------

class TestValidBoundaries:
    """Exact boundary values must be accepted (closed intervals)."""

    def test_latitude_positive_90_is_valid(self):
        """North Pole latitude (+90) must be accepted."""
        validate_coordinates("08MF005", 90.0, 0.0)

    def test_latitude_negative_90_is_valid(self):
        """South Pole latitude (-90) must be accepted."""
        validate_coordinates("08MF005", -90.0, 0.0)

    def test_longitude_positive_180_is_valid(self):
        """Antimeridian longitude (+180) must be accepted."""
        validate_coordinates("08MF005", 0.0, 180.0)

    def test_longitude_negative_180_is_valid(self):
        """Antimeridian longitude (-180) must be accepted."""
        validate_coordinates("08MF005", 0.0, -180.0)

    def test_typical_bc_station_coordinates_are_valid(self):
        """A realistic British Columbia station coordinate pair must be accepted."""
        validate_coordinates("08MH001", 49.2833, -122.7833)

    def test_zero_zero_is_valid(self):
        """Null Island (0°, 0°) is a valid coordinate."""
        validate_coordinates("08MF005", 0.0, 0.0)


# ---------------------------------------------------------------------------
# Invalid out-of-range values — must raise ValueError
# ---------------------------------------------------------------------------

class TestInvalidOutOfRange:
    """Values outside the valid range must raise ValueError."""

    # --- latitude ---

    def test_latitude_999_raises(self):
        """lat=999 is the canonical 'ghost station' example from SEN-49."""
        with pytest.raises(ValueError, match="08MF005"):
            validate_coordinates("08MF005", 999, 0.0)

    def test_latitude_just_above_90_raises(self):
        with pytest.raises(ValueError, match="latitude"):
            validate_coordinates("08MF005", 90.001, 0.0)

    def test_latitude_just_below_minus_90_raises(self):
        with pytest.raises(ValueError, match="latitude"):
            validate_coordinates("08MF005", -90.001, 0.0)

    def test_latitude_minus_91_raises(self):
        with pytest.raises(ValueError, match="-91"):
            validate_coordinates("08MF005", -91, 0.0)

    # --- longitude ---

    def test_longitude_minus_500_raises(self):
        """lon=-500 is the canonical 'ghost station' example from SEN-49."""
        with pytest.raises(ValueError, match="08MF005"):
            validate_coordinates("08MF005", 0.0, -500)

    def test_longitude_just_above_180_raises(self):
        with pytest.raises(ValueError, match="longitude"):
            validate_coordinates("08MF005", 0.0, 180.001)

    def test_longitude_just_below_minus_180_raises(self):
        with pytest.raises(ValueError, match="longitude"):
            validate_coordinates("08MF005", 0.0, -180.001)

    def test_longitude_181_raises(self):
        with pytest.raises(ValueError, match="181"):
            validate_coordinates("08MF005", 0.0, 181)


# ---------------------------------------------------------------------------
# Error message content — must include station_id and the bad value
# ---------------------------------------------------------------------------

class TestErrorMessageContent:
    """Error messages must identify the station and the offending value."""

    def test_error_message_includes_station_id_for_bad_latitude(self):
        station_id = "08MH141"
        bad_lat = 999
        with pytest.raises(ValueError) as exc_info:
            validate_coordinates(station_id, bad_lat, 0.0)
        message = str(exc_info.value)
        assert station_id in message, "Error message must contain the station_id"
        assert str(bad_lat) in message, "Error message must contain the invalid latitude value"

    def test_error_message_includes_station_id_for_bad_longitude(self):
        station_id = "08GA010"
        bad_lon = -500
        with pytest.raises(ValueError) as exc_info:
            validate_coordinates(station_id, 0.0, bad_lon)
        message = str(exc_info.value)
        assert station_id in message, "Error message must contain the station_id"
        assert str(bad_lon) in message, "Error message must contain the invalid longitude value"


# ---------------------------------------------------------------------------
# Partial batch — invalid entries rejected, valid entries processed normally
# ---------------------------------------------------------------------------

class TestPartialBatch:
    """Simulates processing a batch where some stations have invalid coords.

    The validator raises per-station, so a caller that catches ValueError per
    item can process the rest of the batch unimpeded.
    """

    def _process_batch(self, stations: list[dict]) -> tuple[list[str], list[str]]:
        """Mimic the ingest_stations loop: collect successes and errors."""
        successes = []
        errors = []
        for s in stations:
            try:
                validate_coordinates(s["station_id"], s["latitude"], s["longitude"])
                successes.append(s["station_id"])
            except ValueError as exc:
                errors.append(str(exc))
        return successes, errors

    def test_valid_stations_processed_when_batch_contains_invalid_entry(self):
        """Valid stations in the same batch as an invalid one must still be processed."""
        batch = [
            {"station_id": "08MH001", "latitude": 49.2833, "longitude": -122.7833},  # valid
            {"station_id": "08XX999", "latitude": 999,     "longitude": -500},        # invalid
            {"station_id": "08MH005", "latitude": 49.3667, "longitude": -123.0500},  # valid
        ]
        successes, errors = self._process_batch(batch)

        assert "08MH001" in successes, "First valid station must be processed"
        assert "08MH005" in successes, "Third valid station must still be processed"
        assert len(errors) == 1, "Exactly one error should be reported for the invalid station"
        assert "08XX999" in errors[0], "Error must reference the invalid station_id"

    def test_all_invalid_batch_produces_only_errors(self):
        batch = [
            {"station_id": "08XX001", "latitude": 999,  "longitude": 0.0},
            {"station_id": "08XX002", "latitude": 0.0,  "longitude": -500},
        ]
        successes, errors = self._process_batch(batch)
        assert successes == [], "No stations should be processed when all have invalid coords"
        assert len(errors) == 2

    def test_all_valid_batch_produces_no_errors(self):
        batch = [
            {"station_id": "08MH001", "latitude": 49.2833,  "longitude": -122.7833},
            {"station_id": "08MH005", "latitude": -90.0,    "longitude": -180.0},  # boundary
            {"station_id": "08GA010", "latitude":  90.0,    "longitude":  180.0},  # boundary
        ]
        successes, errors = self._process_batch(batch)
        assert errors == [], "No errors expected when all coordinates are valid"
        assert len(successes) == 3
