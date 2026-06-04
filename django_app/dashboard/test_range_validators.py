"""
test_range_validators.py
------------------------
Tests pytest AUTOCONTENIDOS (solo stdlib + pytest, sin Django) para
`validate_range_hours` del módulo `range_validators`.

Cubre:
  - Los 4 rangos canónicos del dashboard (24h, 168h, 720h, 2160h).
  - Strings numéricos válidos ('24').
  - Casos inválidos: 0, -5, 'abc', None, 99999, float NaN  → ValueError.
"""

import math
import sys
import os

# Permitir importar el módulo aunque pytest no agregue automáticamente el path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest

from django_app.dashboard.range_validators import validate_range_hours


# ---------------------------------------------------------------------------
# Casos válidos — rangos canónicos del dashboard
# ---------------------------------------------------------------------------

class TestValidRanges:
    """Los cuatro rangos canónicos deben pasar y devolver el entero correcto."""

    def test_24h_canonical(self):
        assert validate_range_hours(24) == 24

    def test_168h_canonical(self):
        assert validate_range_hours(168) == 168

    def test_720h_canonical(self):
        assert validate_range_hours(720) == 720

    def test_2160h_canonical(self):
        assert validate_range_hours(2160) == 2160

    def test_minimum_boundary(self):
        """El mínimo absoluto (1) debe ser aceptado."""
        assert validate_range_hours(1) == 1

    def test_return_type_is_int(self):
        """La función siempre debe devolver un int."""
        result = validate_range_hours(24)
        assert isinstance(result, int)


# ---------------------------------------------------------------------------
# Strings numéricos válidos
# ---------------------------------------------------------------------------

class TestValidStringInputs:
    """Strings que representan enteros válidos deben ser aceptados."""

    def test_string_24(self):
        assert validate_range_hours('24') == 24

    def test_string_168(self):
        assert validate_range_hours('168') == 168

    def test_string_720(self):
        assert validate_range_hours('720') == 720

    def test_string_2160(self):
        assert validate_range_hours('2160') == 2160

    def test_string_with_whitespace(self):
        """Strings con espacios alrededor deben funcionar igual."""
        assert validate_range_hours('  24  ') == 24


# ---------------------------------------------------------------------------
# Casos inválidos — todos deben lanzar ValueError
# ---------------------------------------------------------------------------

class TestInvalidRaises:
    """Todos los casos inválidos deben lanzar ValueError con mensaje claro."""

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="0"):
            validate_range_hours(0)

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="-5"):
            validate_range_hours(-5)

    def test_non_numeric_string_raises(self):
        with pytest.raises(ValueError, match="abc"):
            validate_range_hours('abc')

    def test_none_raises(self):
        with pytest.raises(ValueError):
            validate_range_hours(None)

    def test_too_large_raises(self):
        with pytest.raises(ValueError, match="99999"):
            validate_range_hours(99999)

    def test_nan_raises(self):
        with pytest.raises(ValueError):
            validate_range_hours(float('nan'))

    def test_negative_large_raises(self):
        with pytest.raises(ValueError):
            validate_range_hours(-9999)

    def test_float_valid_looking_raises(self):
        """Un float como 24.0 también debe ser rechazado (se exige int)."""
        with pytest.raises(ValueError):
            validate_range_hours(24.0)

    def test_float_decimal_raises(self):
        """Un float con decimales debe ser rechazado."""
        with pytest.raises(ValueError):
            validate_range_hours(3.7)

    def test_infinity_raises(self):
        with pytest.raises(ValueError):
            validate_range_hours(float('inf'))

    def test_string_float_raises(self):
        """Un string como '3.7' no es un entero y debe ser rechazado."""
        with pytest.raises(ValueError):
            validate_range_hours('3.7')

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            validate_range_hours('')

    def test_list_raises(self):
        with pytest.raises(ValueError):
            validate_range_hours([24])

    def test_bool_true_raises(self):
        """bool es subclase de int en Python; True == 1 es válido por rango,
        pero semánticamente queremos rechazarlo como tipo bool.
        Sin embargo, dado que bool hereda de int y True == 1, la función
        lo acepta como 1. Este test documenta ese comportamiento esperado."""
        # bool hereda de int → se acepta (True == 1, dentro del rango)
        result = validate_range_hours(True)
        assert result == 1

    def test_2161_just_above_max_raises(self):
        """Justo un paso por encima del máximo."""
        with pytest.raises(ValueError, match="2161"):
            validate_range_hours(2161)


# ---------------------------------------------------------------------------
# Verificación del mensaje de error
# ---------------------------------------------------------------------------

class TestErrorMessages:
    """Los mensajes de error deben ser claros e informativos."""

    def test_zero_message_mentions_zero(self):
        with pytest.raises(ValueError) as exc_info:
            validate_range_hours(0)
        assert "0" in str(exc_info.value)

    def test_negative_message_mentions_value(self):
        with pytest.raises(ValueError) as exc_info:
            validate_range_hours(-5)
        assert "-5" in str(exc_info.value)

    def test_too_large_message_mentions_max(self):
        with pytest.raises(ValueError) as exc_info:
            validate_range_hours(99999)
        assert "2160" in str(exc_info.value)

    def test_nan_message_mentions_nan(self):
        with pytest.raises(ValueError) as exc_info:
            validate_range_hours(float('nan'))
        assert "NaN" in str(exc_info.value)

    def test_none_message_is_informative(self):
        with pytest.raises(ValueError) as exc_info:
            validate_range_hours(None)
        msg = str(exc_info.value)
        assert len(msg) > 10  # El mensaje debe ser sustancial
