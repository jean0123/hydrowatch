# SEN-49: Validate station coordinates on ingestion.
# Latitude must be in the range [-90, 90] and longitude in [-180, 180].
# Values outside these ranges are physically impossible and indicate bad data
# (e.g. lat=999 or lon=-500) that would create "ghost stations" in the
# dashboard.


def validate_coordinates(station_id: str, latitude: float, longitude: float) -> None:
    """Validate that latitude and longitude are within physically valid ranges.

    Parameters
    ----------
    station_id:
        Identifier of the station being validated (used in error messages).
    latitude:
        Latitude value to validate.  Must be in the closed interval [-90, 90].
    longitude:
        Longitude value to validate.  Must be in the closed interval [-180, 180].

    Raises
    ------
    ValueError
        If *latitude* is outside [-90, 90] or *longitude* is outside [-180, 180].
        The error message always includes the ``station_id`` and the offending
        value so that callers can surface a clear, actionable message to
        operators without stopping the rest of the batch.
    """
    if not isinstance(latitude, (int, float)):
        raise ValueError(
            f"Station {station_id!r}: latitude must be a number, "
            f"got {type(latitude).__name__!r}."
        )
    if not isinstance(longitude, (int, float)):
        raise ValueError(
            f"Station {station_id!r}: longitude must be a number, "
            f"got {type(longitude).__name__!r}."
        )

    if not (-90 <= latitude <= 90):
        raise ValueError(
            f"Station {station_id!r}: latitude {latitude!r} is out of range "
            f"[-90, 90]."
        )
    if not (-180 <= longitude <= 180):
        raise ValueError(
            f"Station {station_id!r}: longitude {longitude!r} is out of range "
            f"[-180, 180]."
        )
