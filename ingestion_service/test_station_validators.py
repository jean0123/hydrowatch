"""
test_station_validators.py
--------------------------
Tests pytest para validate_station_id (módulo autocontenido, solo stdlib).
No importa nada de FastAPI ni de la configuración del servicio.
"""

import pytest

from ingestion_service.station_validators import validate_station_id


# ---------------------------------------------------------------------------
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
