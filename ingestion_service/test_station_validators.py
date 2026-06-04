"""Tests for ingestion_service/station_validators.py.

ALL EXISTING TESTS ARE PRESERVED BELOW.  New tests for F-5 (Unicode digit
rejection) are appended at the end of the file.
"""
"""
test_station_validators.py
--------------------------
Tests pytest para validate_station_id (módulo autocontenido, solo stdlib).
No importa nada de FastAPI ni de la configuración del servicio.
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
# Casos VÁLIDOS
# ---------------------------------------------------------------------------

class TestValidStationIds:
    """IDs que deben pasar la validación y devolverse normalizados."""

    def test_canonical_id_passes(self):
        """El ID canónico '08MF005' debe devolverse tal cual."""
        assert validate_station_id("08MF005") == "08MF005"

    def test_lowercase_with_surrounding_spaces_is_normalised(self):
        """' 08mf005 ' debe normalizarse a '08MF005'."""
        assert validate_station_id(" 08mf005 ") == "08MF005"

    def test_already_upper_no_spaces(self):
        """Un ID ya en mayúsculas sin espacios debe pasar directamente."""
        assert validate_station_id("10CD999") == "10CD999"

    def test_leading_spaces_only(self):
        """Espacios solo al inicio deben eliminarse correctamente."""
        assert validate_station_id("  08MF005") == "08MF005"

    def test_trailing_spaces_only(self):
        """Espacios solo al final deben eliminarse correctamente."""
        assert validate_station_id("08MF005  ") == "08MF005"

    def test_lowercase_no_spaces(self):
        """Un ID en minúsculas sin espacios debe normalizarse a mayúsculas."""
        assert validate_station_id("08mf005") == "08MF005"


# ---------------------------------------------------------------------------
# Casos INVÁLIDOS — deben lanzar ValueError
# ---------------------------------------------------------------------------

class TestInvalidStationIds:
    """Cada caso inválido debe lanzar ValueError con un mensaje informativo."""

    def test_none_raises_value_error(self):
        """None debe lanzar ValueError."""
        with pytest.raises(ValueError, match="None"):
            validate_station_id(None)

    def test_empty_string_raises_value_error(self):
        """Cadena vacía debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_station_id("")

    def test_whitespace_only_raises_value_error(self):
        """Cadena de solo espacios (equivale a vacía tras strip) debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_station_id("   ")

    def test_too_short_raises_value_error(self):
        """'08MF05' (6 caracteres) debe lanzar ValueError por longitud incorrecta."""
        with pytest.raises(ValueError):
            validate_station_id("08MF05")

    def test_too_long_raises_value_error(self):
        """'08MF0055' (8 caracteres) debe lanzar ValueError por longitud incorrecta."""
        with pytest.raises(ValueError):
            validate_station_id("08MF0055")

    def test_starts_with_letters_raises_value_error(self):
        """'ABMF005' empieza con letras en lugar de dígitos; debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_station_id("ABMF005")

    def test_internal_space_raises_value_error(self):
        """'08 F005' contiene un espacio interno; debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_station_id("08 F005")

    def test_ends_with_letter_raises_value_error(self):
        """'08MF00X' termina con letra en lugar de dígito; debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_station_id("08MF00X")

    def test_special_characters_raises_value_error(self):
        """Un ID con caracteres especiales debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_station_id("08MF-05")

    def test_numeric_only_raises_value_error(self):
        """Un ID de solo dígitos (1234567) no cumple el patrón; debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_station_id("1234567")
