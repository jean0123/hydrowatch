"""
test_validators.py — Tests pytest para el módulo validators.py.

Archivo PURO: solo stdlib + pytest.
Sin imports de Django ni de ningún framework externo.
"""

import math
import pytest

from dashboard.validators import validate_reading


# ---------------------------------------------------------------------------
# Casos válidos — no deben lanzar ninguna excepción
# ---------------------------------------------------------------------------

class TestValidReadings:
    """Lecturas dentro de los rangos físicos plausibles."""

    def test_zero_values(self):
        """El límite inferior (0, 0) es válido."""
        validate_reading(0, 0)  # no debe lanzar

    def test_typical_reading(self):
        """Valores típicos de operación."""
        validate_reading(5.3, 120.0)

    def test_boundary_water_level_max(self):
        """Exactamente 100 m es válido (límite superior inclusivo)."""
        validate_reading(100, 1000)

    def test_boundary_flow_rate_max(self):
        """Exactamente 50 000 m³/s es válido (límite superior inclusivo)."""
        validate_reading(10, 50000)

    def test_both_at_max_boundary(self):
        """Ambos parámetros en su valor máximo permitido."""
        validate_reading(100, 50000)

    def test_float_precision(self):
        """Valores con decimales dentro del rango."""
        validate_reading(99.9999, 49999.9999)

    def test_integer_inputs(self):
        """Enteros también deben ser aceptados."""
        validate_reading(50, 25000)


# ---------------------------------------------------------------------------
# Casos inválidos — water_level_m
# ---------------------------------------------------------------------------

class TestInvalidWaterLevel:
    """Cada condición inválida para water_level_m lanza ValueError."""

    def test_negative_water_level(self):
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(-0.1, 100)

    def test_large_negative_water_level(self):
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(-999, 0)

    def test_nan_water_level_float(self):
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(float("nan"), 100)

    def test_nan_water_level_math(self):
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(math.nan, 0)

    def test_water_level_above_max(self):
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(100.0001, 0)

    def test_water_level_far_above_max(self):
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(9999, 0)

    def test_water_level_none(self):
        """None no puede convertirse a float → ValueError."""
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(None, 0)

    def test_water_level_string(self):
        """String no numérico → ValueError."""
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading("abc", 0)


# ---------------------------------------------------------------------------
# Casos inválidos — flow_rate_cms
# ---------------------------------------------------------------------------

class TestInvalidFlowRate:
    """Cada condición inválida para flow_rate_cms lanza ValueError."""

    def test_negative_flow_rate(self):
        with pytest.raises(ValueError, match="flow_rate_cms"):
            validate_reading(10, -0.1)

    def test_large_negative_flow_rate(self):
        with pytest.raises(ValueError, match="flow_rate_cms"):
            validate_reading(0, -99999)

    def test_nan_flow_rate_float(self):
        with pytest.raises(ValueError, match="flow_rate_cms"):
            validate_reading(10, float("nan"))

    def test_nan_flow_rate_math(self):
        with pytest.raises(ValueError, match="flow_rate_cms"):
            validate_reading(0, math.nan)

    def test_flow_rate_above_max(self):
        with pytest.raises(ValueError, match="flow_rate_cms"):
            validate_reading(0, 50000.0001)

    def test_flow_rate_far_above_max(self):
        with pytest.raises(ValueError, match="flow_rate_cms"):
            validate_reading(0, 1_000_000)

    def test_flow_rate_none(self):
        """None no puede convertirse a float → ValueError."""
        with pytest.raises(ValueError, match="flow_rate_cms"):
            validate_reading(0, None)

    def test_flow_rate_string(self):
        """String no numérico → ValueError."""
        with pytest.raises(ValueError, match="flow_rate_cms"):
            validate_reading(0, "xyz")


# ---------------------------------------------------------------------------
# Prioridad de validación: water_level_m se valida primero
# ---------------------------------------------------------------------------

class TestValidationOrder:
    """Cuando ambos parámetros son inválidos, water_level_m se detecta primero."""

    def test_both_invalid_water_level_reported_first(self):
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(-1, -1)

    def test_nan_water_level_takes_priority(self):
        with pytest.raises(ValueError, match="water_level_m"):
            validate_reading(float("nan"), float("nan"))
