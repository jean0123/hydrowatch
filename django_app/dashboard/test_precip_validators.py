"""
test_precip_validators.py
=========================
Tests pytest para validate_precipitation_mm (hallazgo F-6).

Solo usa stdlib + pytest; no depende de Django.
"""

import math

import pytest

from dashboard.precip_validators import validate_precipitation_mm


# ---------------------------------------------------------------------------
# Casos VÁLIDOS — deben devolver el float sin lanzar excepciones
# ---------------------------------------------------------------------------

class TestValidValues:
    """Valores que deben pasar la validación sin errores."""

    def test_zero(self):
        """El límite inferior (0) es válido."""
        result = validate_precipitation_mm(0)
        assert result == 0.0
        assert isinstance(result, float)

    def test_zero_float(self):
        """0.0 explícito debe ser aceptado."""
        result = validate_precipitation_mm(0.0)
        assert result == 0.0

    def test_typical_value(self):
        """Un valor intermedio típico (12.5) debe ser aceptado."""
        result = validate_precipitation_mm(12.5)
        assert result == 12.5

    def test_string_numeric(self):
        """Un string numérico válido ('37.2') debe convertirse y aceptarse."""
        result = validate_precipitation_mm("37.2")
        assert result == pytest.approx(37.2)

    def test_upper_bound(self):
        """El límite superior (500) es válido (extremo físico mundial)."""
        result = validate_precipitation_mm(500)
        assert result == 500.0

    def test_upper_bound_float(self):
        """500.0 explícito debe ser aceptado."""
        result = validate_precipitation_mm(500.0)
        assert result == 500.0

    def test_integer_input(self):
        """Enteros válidos deben devolverse como float."""
        result = validate_precipitation_mm(250)
        assert result == 250.0
        assert isinstance(result, float)

    def test_string_zero(self):
        """El string '0' debe ser aceptado."""
        result = validate_precipitation_mm("0")
        assert result == 0.0

    def test_string_upper_bound(self):
        """El string '500' debe ser aceptado."""
        result = validate_precipitation_mm("500")
        assert result == 500.0


# ---------------------------------------------------------------------------
# Casos INVÁLIDOS — deben lanzar ValueError con mensaje descriptivo
# ---------------------------------------------------------------------------

class TestInvalidValues:
    """Valores que deben ser rechazados con ValueError."""

    def test_none_raises(self):
        """None debe lanzar ValueError."""
        with pytest.raises(ValueError, match="None"):
            validate_precipitation_mm(None)

    def test_non_numeric_string_raises(self):
        """Un string no numérico ('abc') debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_precipitation_mm("abc")

    def test_nan_raises(self):
        """float('nan') debe lanzar ValueError."""
        with pytest.raises(ValueError, match="NaN"):
            validate_precipitation_mm(float("nan"))

    def test_nan_math_raises(self):
        """math.nan debe lanzar ValueError."""
        with pytest.raises(ValueError, match="NaN"):
            validate_precipitation_mm(math.nan)

    def test_positive_inf_raises(self):
        """float('inf') debe lanzar ValueError."""
        with pytest.raises(ValueError, match="infinito"):
            validate_precipitation_mm(float("inf"))

    def test_negative_inf_raises(self):
        """float('-inf') debe lanzar ValueError."""
        with pytest.raises(ValueError, match="infinito"):
            validate_precipitation_mm(float("-inf"))

    def test_negative_value_raises(self):
        """-0.1 (negativo) debe lanzar ValueError."""
        with pytest.raises(ValueError, match="negativo"):
            validate_precipitation_mm(-0.1)

    def test_negative_integer_raises(self):
        """-1 (negativo) debe lanzar ValueError."""
        with pytest.raises(ValueError, match="negativo"):
            validate_precipitation_mm(-1)

    def test_above_max_raises(self):
        """500.01 (por encima del máximo físico) debe lanzar ValueError."""
        with pytest.raises(ValueError, match="500"):
            validate_precipitation_mm(500.01)

    def test_large_value_raises(self):
        """Un valor muy grande (9999) debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_precipitation_mm(9999)

    def test_empty_string_raises(self):
        """Un string vacío debe lanzar ValueError."""
        with pytest.raises(ValueError):
            validate_precipitation_mm("")

    def test_list_raises(self):
        """Una lista no debe aceptarse como valor numérico."""
        with pytest.raises(ValueError):
            validate_precipitation_mm([12.5])

    def test_dict_raises(self):
        """Un diccionario no debe aceptarse como valor numérico."""
        with pytest.raises(ValueError):
            validate_precipitation_mm({"mm": 12.5})
