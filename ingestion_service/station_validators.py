# NOTE: re.ASCII flag is required so that \d only matches [0-9] and not
# Unicode digits such as fullwidth digits (U+FF10-U+FF19) or Arabic-Indic
# digits (U+0660-U+0669).  Without this flag the pattern would accept IDs
# that contain non-ASCII digits, which would fail downstream against the
# Environment Canada hydrometric API.
import re

_STATION_ID_RE = re.compile(r"^\d{2}[A-Z]{2}\d{3}$", re.ASCII)


def validate_coordinates(station_id: str, latitude: float, longitude: float) -> None:
    """Validate that latitude and longitude are within valid geographic ranges.

    Latitude must be between -90 and 90 (inclusive).
    Longitude must be between -180 and 180 (inclusive).

    Raises ValueError with a message that includes the station_id and the
    invalid value if either coordinate is out of range.
    """
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


def validate_station_id(station_id: str) -> str:
    """Validate and normalise a hydrometric station ID.

    Normalisation: strip surrounding whitespace, convert to upper-case.
    Valid format: two ASCII digits, two ASCII uppercase letters, three ASCII
    digits (e.g. '08MF005').

    Returns the normalised ID string on success, raises ValueError otherwise.
    """
    if not isinstance(station_id, str):
        raise ValueError(f"Station ID must be a string, got {type(station_id).__name__!r}")

    normalised = station_id.strip().upper()

    if not _STATION_ID_RE.match(normalised):
        raise ValueError(
            f"Invalid station ID {station_id!r}: expected format ##AA### "
            f"(two digits, two letters, three digits), ASCII characters only."
        )

    return normalised
