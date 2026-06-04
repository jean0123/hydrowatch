"""
cooldown_validators.py
======================
Pure-stdlib, Django-free validation for alert-rule cooldown intervals.

A cooldown interval represents the minimum number of minutes that must
pass between two consecutive notification emails for the same alert rule.
Acceptable range: 1 – 1440 minutes (1 minute … 24 hours).
"""

import math

_DEFAULT_COOLDOWN_MINUTES = 60
_MIN_COOLDOWN_MINUTES = 1
_MAX_COOLDOWN_MINUTES = 1440  # 24 hours


def validate_cooldown_minutes(minutes):
    """Validate and return a cooldown interval in minutes.

    Parameters
    ----------
    minutes : int | str | None
        The candidate cooldown value.  Strings that represent whole
        numbers (e.g. ``'120'``) are accepted and converted to ``int``.

    Returns
    -------
    int
        The validated cooldown in minutes.
        Returns ``60`` (the default) when *minutes* is ``None``.

    Raises
    ------
    ValueError
        If *minutes* is zero, negative, non-numeric, NaN, or greater
        than 1440 (24 hours).
    """
    # ── None → default ───────────────────────────────────────────────
    if minutes is None:
        return _DEFAULT_COOLDOWN_MINUTES

    # ── Reject float NaN explicitly (math.nan, float('nan'), …) ──────
    if isinstance(minutes, float):
        if math.isnan(minutes):
            raise ValueError(
                "cooldown_minutes must be a whole number between "
                f"{_MIN_COOLDOWN_MINUTES} and {_MAX_COOLDOWN_MINUTES}; "
                "got NaN."
            )
        # Reject non-integer floats silently converted to int would lose
        # precision – treat any float path as non-numeric.
        raise ValueError(
            "cooldown_minutes must be an integer or a numeric string, "
            f"not a float ({minutes!r}).  "
            f"Accepted range: {_MIN_COOLDOWN_MINUTES}–{_MAX_COOLDOWN_MINUTES}."
        )

    # ── String → int conversion ───────────────────────────────────────
    if isinstance(minutes, str):
        stripped = minutes.strip()
        if not stripped:
            raise ValueError(
                "cooldown_minutes must not be an empty string.  "
                f"Accepted range: {_MIN_COOLDOWN_MINUTES}–{_MAX_COOLDOWN_MINUTES}."
            )
        try:
            minutes = int(stripped)
        except ValueError:
            raise ValueError(
                f"cooldown_minutes must be a numeric string, got {stripped!r}.  "
                f"Accepted range: {_MIN_COOLDOWN_MINUTES}–{_MAX_COOLDOWN_MINUTES}."
            )

    # ── Must be an integer at this point ─────────────────────────────
    if not isinstance(minutes, int):
        raise ValueError(
            f"cooldown_minutes must be an integer or a numeric string, "
            f"got {minutes!r} ({type(minutes).__name__}).  "
            f"Accepted range: {_MIN_COOLDOWN_MINUTES}–{_MAX_COOLDOWN_MINUTES}."
        )

    # ── Range check ───────────────────────────────────────────────────
    if minutes <= 0:
        raise ValueError(
            f"cooldown_minutes must be at least {_MIN_COOLDOWN_MINUTES}, "
            f"got {minutes}.  Zero and negative values are not allowed."
        )

    if minutes > _MAX_COOLDOWN_MINUTES:
        raise ValueError(
            f"cooldown_minutes must be at most {_MAX_COOLDOWN_MINUTES} "
            f"(24 hours), got {minutes}."
        )

    return minutes
