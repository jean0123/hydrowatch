"""Tests for ingestion_service/station_validators.py and main.py helpers.

ALL EXISTING TESTS ARE PRESERVED BELOW.  New tests for F-5 (Unicode digit
rejection) are appended at the end of the file.  Tests for F-1 (input
validation in _generate_demo_readings) are appended after that.
"""

import pytest

from ingestion_service.station_validators import validate_station_id
from ingestion_service.main import _generate_demo_readings


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
# F-1 – Input validation in _generate_demo_readings (NEW)
# ---------------------------------------------------------------------------

class TestGenerateDemoReadingsValidation:
    """_generate_demo_readings must reject invalid ``hours`` values.

    Finding F-1: the function previously accepted any value for ``hours``
    (zero, negative numbers, floats, strings) without raising an error,
    producing silently wrong or empty results.  After the fix it must raise
    a ``ValueError`` with a descriptive message for invalid inputs.
    """

    # --- invalid hours ---

    def test_zero_hours_raises(self):
        """hours=0 must be rejected – there is nothing to generate."""
        with pytest.raises(ValueError, match="hours must be >= 1"):
            _generate_demo_readings("08MF005", 0)

    def test_negative_hours_raises(self):
        """Negative hours make no sense and must raise ValueError."""
        with pytest.raises(ValueError, match="hours must be >= 1"):
            _generate_demo_readings("08MF005", -5)

    def test_float_hours_raises(self):
        """A float (e.g. 24.0) is not a valid int and must raise ValueError."""
        with pytest.raises(ValueError, match="hours must be a positive integer"):
            _generate_demo_readings("08MF005", 24.0)

    def test_string_hours_raises(self):
        """A string (e.g. '24') must raise ValueError."""
        with pytest.raises(ValueError, match="hours must be a positive integer"):
            _generate_demo_readings("08MF005", "24")

    def test_none_hours_raises(self):
        """None must raise ValueError."""
        with pytest.raises(ValueError, match="hours must be a positive integer"):
            _generate_demo_readings("08MF005", None)

    def test_bool_hours_raises(self):
        """bool is a subclass of int in Python but must be rejected here."""
        with pytest.raises(ValueError, match="hours must be a positive integer"):
            _generate_demo_readings("08MF005", True)

    # --- valid hours ---

    def test_one_hour_returns_one_reading(self):
        """hours=1 is the minimum valid value; should return exactly 1 reading."""
        readings = _generate_demo_readings("08MF005", 1)
        assert len(readings) == 1

    def test_positive_hours_returns_correct_count(self):
        """hours=N should return exactly N readings."""
        readings = _generate_demo_readings("08MF005", 12)
        assert len(readings) == 12

    def test_reading_has_expected_keys(self):
        """Each returned reading dict must contain the required keys."""
        readings = _generate_demo_readings("08MF005", 3)
        for r in readings:
            assert "timestamp" in r
            assert "water_level" in r
            assert "flow_rate" in r
