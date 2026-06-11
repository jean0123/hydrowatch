"""
test_tasks_cooldown_integration.py
====================================
Tests that verify validate_cooldown_minutes is wired into the tasks module
and that the cooldown constants are computed correctly.

These tests are PURE (no Django DB access needed) and exercise the actual
code path: tasks._ALERT_COOLDOWN_MINUTES and tasks._ALERT_COOLDOWN_SECONDS.
"""

import importlib
import sys
import types

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_tasks_with_setting(cooldown_setting):
    """
    Import (or re-import) dashboard.tasks with a fake Django settings that
    has ALERT_COOLDOWN_MINUTES set to *cooldown_setting*.

    Returns the freshly-imported module so we can inspect its module-level
    constants.
    """
    # Build a minimal fake 'django.conf.settings' that supports getattr.
    fake_settings = types.SimpleNamespace(
        ALERT_COOLDOWN_MINUTES=cooldown_setting,
    )

    # Patch sys.modules so that when tasks.py does
    #   from django.conf import settings
    # it gets our fake object.
    import django.conf as django_conf
    original_settings = django_conf.settings

    # We need to temporarily replace the settings proxy.
    # SimpleNamespace doesn't have __getattr__ for missing attrs, so we wrap:
    class FakeSettings:
        def __init__(self, cd):
            self._cd = cd

        def __getattr__(self, name):
            if name == "ALERT_COOLDOWN_MINUTES":
                return self._cd
            raise AttributeError(name)

    django_conf.settings = FakeSettings(cooldown_setting)

    # Remove cached module so it re-executes module-level code.
    sys.modules.pop("dashboard.tasks", None)

    try:
        import dashboard.tasks as tasks_mod
        return tasks_mod
    finally:
        # Restore original settings
        django_conf.settings = original_settings
        # Remove the re-imported module so subsequent tests start fresh.
        sys.modules.pop("dashboard.tasks", None)


# ---------------------------------------------------------------------------
# Tests: module-level constants
# ---------------------------------------------------------------------------

class TestTasksCooldownIntegration:
    """Verify that tasks.py uses validate_cooldown_minutes for its cooldown."""

    def test_default_cooldown_when_setting_absent(self):
        """When ALERT_COOLDOWN_MINUTES is not set (None), tasks uses 60 min."""
        tasks = _import_tasks_with_setting(None)
        assert tasks._ALERT_COOLDOWN_MINUTES == 60
        assert tasks._ALERT_COOLDOWN_SECONDS == 3600

    def test_valid_custom_cooldown(self):
        """A valid custom cooldown (e.g. 30) is accepted and wired in."""
        tasks = _import_tasks_with_setting(30)
        assert tasks._ALERT_COOLDOWN_MINUTES == 30
        assert tasks._ALERT_COOLDOWN_SECONDS == 1800

    def test_valid_minimum_cooldown(self):
        """The minimum valid cooldown (1 minute) is accepted."""
        tasks = _import_tasks_with_setting(1)
        assert tasks._ALERT_COOLDOWN_MINUTES == 1
        assert tasks._ALERT_COOLDOWN_SECONDS == 60

    def test_valid_maximum_cooldown(self):
        """The maximum valid cooldown (1440 minutes) is accepted."""
        tasks = _import_tasks_with_setting(1440)
        assert tasks._ALERT_COOLDOWN_MINUTES == 1440
        assert tasks._ALERT_COOLDOWN_SECONDS == 86400

    def test_zero_cooldown_raises_at_import(self):
        """A zero cooldown is invalid and raises ValueError when tasks loads."""
        with pytest.raises(ValueError, match="mayor que cero"):
            _import_tasks_with_setting(0)

    def test_negative_cooldown_raises_at_import(self):
        """A negative cooldown raises ValueError when tasks loads."""
        with pytest.raises(ValueError, match="mayor que cero"):
            _import_tasks_with_setting(-10)

    def test_above_maximum_cooldown_raises_at_import(self):
        """A cooldown > 1440 raises ValueError when tasks loads."""
        with pytest.raises(ValueError, match="1440"):
            _import_tasks_with_setting(1441)

    def test_non_numeric_string_raises_at_import(self):
        """A non-numeric string cooldown raises ValueError when tasks loads."""
        with pytest.raises(ValueError, match="numérico"):
            _import_tasks_with_setting("not-a-number")

    def test_string_numeric_cooldown_accepted(self):
        """A string numeric cooldown (e.g. '120') is accepted."""
        tasks = _import_tasks_with_setting("120")
        assert tasks._ALERT_COOLDOWN_MINUTES == 120
        assert tasks._ALERT_COOLDOWN_SECONDS == 7200

    def test_boolean_cooldown_raises_at_import(self):
        """True/False are not valid cooldown values."""
        with pytest.raises(ValueError, match="booleano"):
            _import_tasks_with_setting(True)

    def test_validate_cooldown_minutes_is_imported_in_tasks(self):
        """tasks module imports validate_cooldown_minutes (wired-in check)."""
        tasks = _import_tasks_with_setting(None)
        # The function must be reachable from the module namespace
        assert hasattr(tasks, "validate_cooldown_minutes"), (
            "validate_cooldown_minutes must be imported in dashboard/tasks.py"
        )
