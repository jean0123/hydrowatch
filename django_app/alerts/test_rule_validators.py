"""
test_rule_validators.py
-----------------------
Tests pytest para validate_alert_rule.
Archivos PUROS — solo stdlib + pytest, sin imports de Django.
"""

import math
import pytest

from django_app.alerts.rule_validators import validate_alert_rule


# ---------------------------------------------------------------------------
# Casos VÁLIDOS
# ---------------------------------------------------------------------------

class TestValidCombinations:
    def test_integer_threshold_gt(self):
        result = validate_alert_rule(10, 'gt', 'user@example.com')
        assert result == (10.0, 'gt', 'user@example.com')

    def test_float_threshold_gte(self):
        result = validate_alert_rule(3.14, 'gte', 'alert@monitor.io')
        assert result == (3.14, 'gte', 'alert@monitor.io')

    def test_string_numeric_threshold_lt(self):
        result = validate_alert_rule('42', 'lt', 'ops@company.org')
        assert result == (42.0, 'lt', 'ops@company.org')

    def test_negative_threshold_lte(self):
        result = validate_alert_rule(-5.5, 'lte', 'admin@sub.domain.com')
        assert result == (-5.5, 'lte', 'admin@sub.domain.com')

    def test_zero_threshold_eq(self):
        result = validate_alert_rule(0, 'eq', 'zero@test.net')
        assert result == (0.0, 'eq', 'zero@test.net')

    def test_returns_float(self):
        threshold_float, _, _ = validate_alert_rule(7, 'gt', 'a@b.com')
        assert isinstance(threshold_float, float)

    def test_all_operators_accepted(self):
        for op in ('gt', 'gte', 'lt', 'lte', 'eq'):
            threshold_float, operator, email = validate_alert_rule(1, op, 'a@b.com')
            assert operator == op


# ---------------------------------------------------------------------------
# Casos INVÁLIDOS — threshold
# ---------------------------------------------------------------------------

class TestInvalidThreshold:
    def test_non_numeric_string(self):
        with pytest.raises(ValueError, match="umbral"):
            validate_alert_rule('abc', 'gt', 'user@example.com')

    def test_nan_float(self):
        with pytest.raises(ValueError, match="NaN"):
            validate_alert_rule(float('nan'), 'gt', 'user@example.com')

    def test_nan_math(self):
        with pytest.raises(ValueError, match="NaN"):
            validate_alert_rule(math.nan, 'gt', 'user@example.com')

    def test_positive_infinity(self):
        with pytest.raises(ValueError, match="infinito"):
            validate_alert_rule(float('inf'), 'gt', 'user@example.com')

    def test_negative_infinity(self):
        with pytest.raises(ValueError, match="infinito"):
            validate_alert_rule(float('-inf'), 'gt', 'user@example.com')

    def test_math_inf(self):
        with pytest.raises(ValueError, match="infinito"):
            validate_alert_rule(math.inf, 'gt', 'user@example.com')

    def test_none_threshold(self):
        with pytest.raises(ValueError):
            validate_alert_rule(None, 'gt', 'user@example.com')

    def test_empty_string_threshold(self):
        with pytest.raises(ValueError):
            validate_alert_rule('', 'gt', 'user@example.com')

    def test_list_threshold(self):
        with pytest.raises(ValueError):
            validate_alert_rule([1, 2], 'gt', 'user@example.com')


# ---------------------------------------------------------------------------
# Casos INVÁLIDOS — operator
# ---------------------------------------------------------------------------

class TestInvalidOperator:
    def test_between_operator(self):
        with pytest.raises(ValueError, match="operador"):
            validate_alert_rule(10, 'between', 'user@example.com')

    def test_uppercase_gt(self):
        with pytest.raises(ValueError, match="operador"):
            validate_alert_rule(10, 'GT', 'user@example.com')

    def test_empty_operator(self):
        with pytest.raises(ValueError, match="operador"):
            validate_alert_rule(10, '', 'user@example.com')

    def test_ne_operator(self):
        with pytest.raises(ValueError, match="operador"):
            validate_alert_rule(10, 'ne', 'user@example.com')

    def test_greater_than_symbol(self):
        with pytest.raises(ValueError, match="operador"):
            validate_alert_rule(10, '>', 'user@example.com')


# ---------------------------------------------------------------------------
# Casos INVÁLIDOS — email
# ---------------------------------------------------------------------------

class TestInvalidEmail:
    def test_no_at_sign(self):
        with pytest.raises(ValueError, match="email"):
            validate_alert_rule(10, 'gt', 'sin-arroba')

    def test_space_in_email(self):
        with pytest.raises(ValueError, match="email"):
            validate_alert_rule(10, 'gt', 'a @b.c')

    def test_no_domain_dot(self):
        with pytest.raises(ValueError, match="email"):
            validate_alert_rule(10, 'gt', 'user@nodot')

    def test_empty_email(self):
        with pytest.raises(ValueError, match="email"):
            validate_alert_rule(10, 'gt', '')

    def test_only_at_sign(self):
        with pytest.raises(ValueError, match="email"):
            validate_alert_rule(10, 'gt', '@')

    def test_space_before_at(self):
        with pytest.raises(ValueError, match="email"):
            validate_alert_rule(10, 'gt', ' user@domain.com')

    def test_space_after_domain(self):
        with pytest.raises(ValueError, match="email"):
            validate_alert_rule(10, 'gt', 'user@domain.com ')
