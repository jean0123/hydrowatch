"""Tests for ingestion_service/station_validators.py.

ALL EXISTING TESTS ARE PRESERVED BELOW.  New tests for F-5 (Unicode digit
rejection) are appended at the end of the file.
"""

import pytest

from ingestion_service.station_validators import validate_station_id, validate_coordinates


# ---------------------------------------------------------------------------
# Existing tests (preserved verbatim)
# ---------------------------------------------------------------------------

class TestValidStationIds:
    """Valid IDs should be returned normalised (stripped + uppercased)."""

    def test_canonical_id(self):
        assert validate_station_id("08MF005") == "08MF005"

    def test_lowercase_letters_are_uppercased(self):
        assert validate_station_id("08mf005") == "08MF005"

    def test_leading_trailing_whitespace_stripped(self):
        assert validate_station_id(" 08MF005 ") == "08MF005"

    def test_lowercase_with_whitespace(self):
        assert validate_station_id(" 08mf005 ") == "08MF005"

    def test_different_valid_id(self):
        assert validate_station_id("02HA001") == "02HA001"

    def test_all_uppercase_no_whitespace(self):
        assert validate_station_id("10CD002") == "10CD002"


class TestInvalidStationIds:
    """Invalid IDs should raise ValueError."""

    def test_empty_string(self):
        with pytest.raises(ValueError):
            validate_station_id("")

    def test_too_short(self):
        with pytest.raises(ValueError):
            validate_station_id("08MF05")

    def test_too_long(self):
        with pytest.raises(ValueError):
            validate_station_id("08MF0055")

    def test_letters_where_digits_expected_prefix(self):
        with pytest.raises(ValueError):
            validate_station_id("ABMF005")

    def test_digits_where_letters_expected(self):
        with pytest.raises(ValueError):
            validate_station_id("0812005")

    def test_special_characters(self):
        with pytest.raises(ValueError):
            validate_station_id("08-F005")

    def test_none_raises_value_error(self):
        with pytest.raises(ValueError):
            validate_station_id(None)

    def test_integer_raises_value_error(self):
        with pytest.raises(ValueError):
            validate_station_id(12345)

    def test_whitespace_only(self):
        with pytest.raises(ValueError):
            validate_station_id("   ")


# ---------------------------------------------------------------------------
# F-5 – Unicode digit rejection tests (NEW)
# ---------------------------------------------------------------------------

class TestUnicodeDigitsRejected:
    """IDs containing non-ASCII (Unicode) digits must be rejected.

    Environment Canada hydrometric station IDs are ASCII-only.  Without
    re.ASCII the \\d pattern would silently accept Unicode digit characters
    (e.g. fullwidth digits U+FF10-U+FF19, Arabic-Indic digits U+0660-U+0669)
    producing IDs that look correct but break downstream API calls.
    """

    def test_fullwidth_digits_rejected(self):
        """U+FF10 (０) and U+FF18 (８) are fullwidth digits, not ASCII."""
        with pytest.raises(ValueError):
            validate_station_id("\uff10\uff18MF005")  # ０８MF005

    def test_arabic_indic_digit_rejected(self):
        """U+0660 (٠) is an Arabic-Indic zero, not an ASCII digit."""
        with pytest.raises(ValueError):
            validate_station_id("08MF00\u0660")  # 08MF00٠

    def test_ascii_valid_id_still_passes(self):
        """Plain ASCII ID must continue to pass after the fix."""
        assert validate_station_id("08MF005") == "08MF005"

    def test_ascii_valid_id_with_whitespace_and_lowercase_still_passes(self):
        """Normalisation (strip + upper) must still work for ASCII IDs."""
        assert validate_station_id(" 08mf005 ") == "08MF005"


# ---------------------------------------------------------------------------
# STR-MQAKU5HN – Coordinate validation tests (NEW)
# ---------------------------------------------------------------------------

class TestValidateCoordinates:
    """Coordinate validation: lat ∈ [-90, 90], lon ∈ [-180, 180]."""

    # --- Boundary values that MUST be accepted ---

    def test_lat_positive_boundary_valid(self):
        """Latitude of exactly +90 is valid."""
        validate_coordinates("08MF005", 90.0, 0.0)

    def test_lat_negative_boundary_valid(self):
        """Latitude of exactly -90 is valid."""
        validate_coordinates("08MF005", -90.0, 0.0)

    def test_lon_positive_boundary_valid(self):
        """Longitude of exactly +180 is valid."""
        validate_coordinates("08MF005", 0.0, 180.0)

    def test_lon_negative_boundary_valid(self):
        """Longitude of exactly -180 is valid."""
        validate_coordinates("08MF005", 0.0, -180.0)

    def test_typical_valid_coordinates(self):
        """Typical real-world coordinate pair is accepted without error."""
        validate_coordinates("08MH001", 49.2833, -122.7833)

    # --- Values that MUST be rejected ---

    def test_lat_above_range_raises(self):
        """Latitude > 90 must raise ValueError with station_id and value."""
        with pytest.raises(ValueError) as exc_info:
            validate_coordinates("08MF005", 999.0, 0.0)
        msg = str(exc_info.value)
        assert "08MF005" in msg
        assert "999" in msg

    def test_lat_below_range_raises(self):
        """Latitude < -90 must raise ValueError with station_id and value."""
        with pytest.raises(ValueError) as exc_info:
            validate_coordinates("08MF005", -91.0, 0.0)
        msg = str(exc_info.value)
        assert "08MF005" in msg
        assert "-91" in msg

    def test_lon_above_range_raises(self):
        """Longitude > 180 must raise ValueError with station_id and value."""
        with pytest.raises(ValueError) as exc_info:
            validate_coordinates("08MF005", 0.0, 181.0)
        msg = str(exc_info.value)
        assert "08MF005" in msg
        assert "181" in msg

    def test_lon_below_range_raises(self):
        """Longitude < -180 must raise ValueError with station_id and value."""
        with pytest.raises(ValueError) as exc_info:
            validate_coordinates("08MF005", 0.0, -500.0)
        msg = str(exc_info.value)
        assert "08MF005" in msg
        assert "-500" in msg

    def test_error_message_contains_station_id(self):
        """Error message must include the station_id for easy diagnosis."""
        station = "08GA010"
        with pytest.raises(ValueError) as exc_info:
            validate_coordinates(station, 999.0, 0.0)
        assert station in str(exc_info.value)

    def test_valid_station_in_batch_not_affected_by_invalid(self):
        """Valid coordinates do not raise; only invalid ones raise.

        This simulates the partial-batch scenario: a valid reading must pass
        through even when another reading in the same batch is rejected.
        """
        stations = [
            {"station_id": "08MH001", "latitude": 49.28, "longitude": -122.78},  # valid
            {"station_id": "08XX999", "latitude": 999.0, "longitude": -500.0},   # invalid
            {"station_id": "08MH005", "latitude": 49.37, "longitude": -123.05},  # valid
        ]
        errors = []
        processed = []
        for s in stations:
            try:
                validate_coordinates(s["station_id"], s["latitude"], s["longitude"])
                processed.append(s["station_id"])
            except ValueError as e:
                errors.append(str(e))

        assert processed == ["08MH001", "08MH005"], "Only valid stations should be processed"
        assert len(errors) == 1, "Exactly one error for the invalid station"
        assert "08XX999" in errors[0]
