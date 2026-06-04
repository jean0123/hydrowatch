"""
param_validators.py – Autocontained pagination parameter validation (stdlib only).

No Django, no DRF imports.  Pure functions for use anywhere in the project.
"""

import math

_DEFAULT_LIMIT = 50
_MIN_LIMIT = 1
_MAX_LIMIT = 500


def validate_page_limit(limit):
    """Validate and return an integer page-limit value.

    Rules
    -----
    - If *limit* is ``None``, return the default (50).
    - If *limit* is an ``int`` or a string that represents a whole number,
      convert it and verify it falls within [1, 500].
    - Raise ``ValueError`` with a descriptive message for any invalid input:
      zero, negative, non-numeric strings, NaN, or values above 500.

    Parameters
    ----------
    limit : int | str | None
        The raw value received from the request parameter.

    Returns
    -------
    int
        A validated integer in the range [1, 500].

    Raises
    ------
    ValueError
        When *limit* cannot be interpreted as a valid page limit.
    """
    # --- None → default ---------------------------------------------------
    if limit is None:
        return _DEFAULT_LIMIT

    # --- Reject float NaN/Inf explicitly (floats are not valid limits) ----
    if isinstance(limit, float):
        if math.isnan(limit):
            raise ValueError(
                "Invalid page limit: NaN is not allowed. "
                f"Provide an integer between {_MIN_LIMIT} and {_MAX_LIMIT}."
            )
        if math.isinf(limit):
            raise ValueError(
                "Invalid page limit: infinite values are not allowed. "
                f"Provide an integer between {_MIN_LIMIT} and {_MAX_LIMIT}."
            )
        # Even finite floats are rejected; limits must be whole numbers.
        raise ValueError(
            f"Invalid page limit: float values are not allowed ({limit!r}). "
            f"Provide an integer between {_MIN_LIMIT} and {_MAX_LIMIT}."
        )

    # --- Convert string → int (or reject non-numeric) ---------------------
    if isinstance(limit, str):
        # Reject strings that look like NaN or floats explicitly
        stripped = limit.strip()
        if stripped.lower() == "nan":
            raise ValueError(
                "Invalid page limit: 'nan' is not a valid integer. "
                f"Provide an integer between {_MIN_LIMIT} and {_MAX_LIMIT}."
            )
        try:
            limit = int(stripped)
        except ValueError:
            raise ValueError(
                f"Invalid page limit: {stripped!r} is not a valid integer. "
                f"Provide an integer between {_MIN_LIMIT} and {_MAX_LIMIT}."
            )

    # --- At this point limit must be an int (or int-like) -----------------
    if not isinstance(limit, int):
        raise ValueError(
            f"Invalid page limit: expected an integer or numeric string, "
            f"got {type(limit).__name__!r} ({limit!r})."
        )

    # --- Range check ------------------------------------------------------
    if limit <= 0:
        raise ValueError(
            f"Invalid page limit: {limit} is not positive. "
            f"Provide an integer between {_MIN_LIMIT} and {_MAX_LIMIT}."
        )
    if limit > _MAX_LIMIT:
        raise ValueError(
            f"Invalid page limit: {limit} exceeds the maximum allowed value "
            f"of {_MAX_LIMIT}."
        )

    return limit
