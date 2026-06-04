"""Tests for ingestion_service/station_validators.py.

ALL EXISTING TESTS ARE PRESERVED BELOW.  New tests for F-5 (Unicode digit
rejection) are appended at the end of the file.
"""
import pytest

from ingestion_service.station_validators import validate_station_id


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
