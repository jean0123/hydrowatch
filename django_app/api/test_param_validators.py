"""
Tests for django_app/api/param_validators.py  (F-7 – pagination validation).

Pure pytest, no Django/DRF dependencies required.
"""

import math

import pytest

from .param_validators import validate_page_limit


# ---------------------------------------------------------------------------
# Valid inputs – must return the integer value unchanged
# ---------------------------------------------------------------------------

class TestValidInputs:
    def test_minimum_boundary(self):
        assert validate_page_limit(1) == 1

    def test_default_numeric_value(self):
        assert validate_page_limit(50) == 50

    def test_numeric_string(self):
        assert validate_page_limit("200") == 200

    def test_maximum_boundary(self):
        assert validate_page_limit(500) == 500

    def test_numeric_string_minimum(self):
        assert validate_page_limit("1") == 1

    def test_numeric_string_maximum(self):
        assert validate_page_limit("500") == 500

    def test_midrange_value(self):
        assert validate_page_limit(100) == 100


# ---------------------------------------------------------------------------
# None → default (50)
# ---------------------------------------------------------------------------

class TestNoneReturnsDefault:
    def test_none_returns_50(self):
        assert validate_page_limit(None) == 50


# ---------------------------------------------------------------------------
# Invalid inputs – must raise ValueError
# ---------------------------------------------------------------------------

class TestInvalidInputsRaiseValueError:
    def test_zero_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit(0)

    def test_negative_one_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit(-1)

    def test_large_negative_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit(-999)

    def test_non_numeric_string_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit("abc")

    def test_above_max_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit(501)

    def test_well_above_max_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit(10_000)

    def test_nan_float_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit(float("nan"))

    def test_nan_string_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit("nan")

    def test_nan_string_upper_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit("NaN")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit("")

    def test_whitespace_string_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit("   ")

    def test_float_string_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit("3.5")

    def test_zero_string_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit("0")

    def test_negative_string_raises(self):
        with pytest.raises(ValueError, match="page limit"):
            validate_page_limit("-1")
