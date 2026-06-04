"""
test_cooldown_validators.py
===========================
Pytest suite for django_app/alerts/cooldown_validators.py.

Pure stdlib + pytest — no Django dependency required.
"""

import math

import pytest

from alerts.cooldown_validators import validate_cooldown_minutes


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

class TestValidCooldownValues:
    """Values that must be accepted and returned as int."""

    def test_minimum_boundary(self):
        assert validate_cooldown_minutes(1) == 1

    def test_typical_default(self):
        assert validate_cooldown_minutes(60) == 60

    def test_string_numeric(self):
        result = validate_cooldown_minutes("120")
        assert result == 120
        assert isinstance(result, int)

    def test_maximum_boundary(self):
        assert validate_cooldown_minutes(1440) == 1440

    def test_string_with_whitespace(self):
        """Strings with surrounding whitespace should still parse."""
        assert validate_cooldown_minutes("  30  ") == 30

    def test_mid_range_value(self):
        assert validate_cooldown_minutes(720) == 720  # 12 hours


class TestNoneReturnsDefault:
    """None must silently return the default (60)."""

    def test_none_returns_60(self):
        result = validate_cooldown_minutes(None)
        assert result == 60

    def test_none_returns_int(self):
        assert isinstance(validate_cooldown_minutes(None), int)


# ─────────────────────────────────────────────────────────────────────────────
# Invalid values – each must raise ValueError
# ─────────────────────────────────────────────────────────────────────────────

class TestZeroRaisesValueError:
    def test_zero(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(0)


class TestNegativeRaisesValueError:
    def test_negative_five(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(-5)

    def test_negative_one(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(-1)

    def test_large_negative(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(-9999)


class TestNonNumericStringRaisesValueError:
    def test_alpha_string(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes("abc")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes("")

    def test_whitespace_only(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes("   ")

    def test_float_string(self):
        """A string like '1.5' is not a whole-number string."""
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes("1.5")


class TestAboveMaximumRaisesValueError:
    def test_one_above_max(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(1441)

    def test_absurdly_large(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(525_600)  # one year in minutes


class TestNaNRaisesValueError:
    def test_float_nan(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(float("nan"))

    def test_math_nan(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(math.nan)


class TestInvalidTypesRaiseValueError:
    def test_list(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes([60])

    def test_dict(self):
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes({"minutes": 60})

    def test_plain_float(self):
        """Plain floats (even valid-looking ones) are rejected."""
        with pytest.raises(ValueError, match="cooldown_minutes"):
            validate_cooldown_minutes(60.0)
