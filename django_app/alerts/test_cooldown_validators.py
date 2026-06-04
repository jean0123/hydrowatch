"""
test_cooldown_validators.py
===========================
Tests pytest para validate_cooldown_minutes (solo stdlib + pytest).
Cubre los criterios de aceptación de la historia F-9.
"""

import math

import pytest

from alerts.cooldown_validators import validate_cooldown_minutes


# ---------------------------------------------------------------------------
# Casos válidos — deben devolver el entero sin lanzar excepción
# ---------------------------------------------------------------------------

class TestValidValues:
    def test_minimum_boundary(self):
        """1 es el mínimo permitido."""
        assert validate_cooldown_minutes(1) == 1

    def test_default_value_as_int(self):
        """60 es el valor por defecto y debe pasar como entero normal."""
        assert validate_cooldown_minutes(60) == 60

    def test_string_numeric(self):
        """'120' como string numérico debe convertirse a 120."""
        assert validate_cooldown_minutes("120") == 120

    def test_maximum_boundary(self):
        """1440 es el máximo permitido (24 horas)."""
        assert validate_cooldown_minutes(1440) == 1440

    def test_string_with_whitespace(self):
        """Strings con espacios alrededor deben ser aceptados."""
        assert validate_cooldown_minutes("  30  ") == 30

    def test_string_minimum(self):
        """'1' como string es válido."""
        assert validate_cooldown_minutes("1") == 1

    def test_string_maximum(self):
        """'1440' como string es válido."""
        assert validate_cooldown_minutes("1440") == 1440


# ---------------------------------------------------------------------------
# None → debe devolver 60 (el default)
# ---------------------------------------------------------------------------

class TestNoneReturnsDefault:
    def test_none_returns_60(self):
        """None debe devolver el cooldown por defecto: 60."""
        assert validate_cooldown_minutes(None) == 60


# ---------------------------------------------------------------------------
# Casos inválidos — deben lanzar ValueError con mensaje claro
# ---------------------------------------------------------------------------

class TestInvalidValues:
    def test_zero_raises(self):
        """0 no está permitido (debe ser >= 1)."""
        with pytest.raises(ValueError, match="mayor que cero"):
            validate_cooldown_minutes(0)

    def test_negative_raises(self):
        """-5 es negativo y no está permitido."""
        with pytest.raises(ValueError, match="mayor que cero"):
            validate_cooldown_minutes(-5)

    def test_non_numeric_string_raises(self):
        """'abc' no es numérico y debe lanzar ValueError."""
        with pytest.raises(ValueError, match="numérico"):
            validate_cooldown_minutes("abc")

    def test_above_maximum_raises(self):
        """1441 supera el máximo de 1440 y debe lanzar ValueError."""
        with pytest.raises(ValueError, match="1440"):
            validate_cooldown_minutes(1441)

    def test_nan_raises(self):
        """float('nan') no es válido y debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_cooldown_minutes(float("nan"))

    def test_negative_large_raises(self):
        """Valores muy negativos también deben ser rechazados."""
        with pytest.raises(ValueError, match="mayor que cero"):
            validate_cooldown_minutes(-1000)

    def test_very_large_value_raises(self):
        """Valores absurdamente grandes (años) deben ser rechazados."""
        with pytest.raises(ValueError, match="1440"):
            validate_cooldown_minutes(525600)  # minutos en un año

    def test_empty_string_raises(self):
        """Un string vacío no es un entero válido."""
        with pytest.raises(ValueError):
            validate_cooldown_minutes("")

    def test_float_nan_math_raises(self):
        """math.nan también debe ser rechazado."""
        with pytest.raises(ValueError):
            validate_cooldown_minutes(math.nan)

    def test_string_float_raises(self):
        """'12.5' no es un entero válido."""
        with pytest.raises(ValueError):
            validate_cooldown_minutes("12.5")

    def test_boolean_raises(self):
        """True/False son bool, no deben ser aceptados como cooldown."""
        with pytest.raises(ValueError):
            validate_cooldown_minutes(True)
