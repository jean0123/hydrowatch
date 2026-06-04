# NOTE: re.ASCII flag is required so that \d only matches [0-9] and not
# Unicode digits such as fullwidth digits (U+FF10-U+FF19) or Arabic-Indic
# digits (U+0660-U+0669).  Without this flag the pattern would accept IDs
# that contain non-ASCII digits, which would fail downstream against the
# Environment Canada hydrometric API.
import re

_STATION_ID_RE = re.compile(r"^\d{2}[A-Z]{2}\d{3}$", re.ASCII)


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
"""
station_validators.py
---------------------
Módulo autocontenido (solo stdlib) para validar IDs de estación hidrométrica
de Environment Canada.

Patrón esperado: 2 dígitos + 2 letras mayúsculas + 3 dígitos  (ej. 08MF005)
"""

import re

# Patrón: DD LL DDD  (D=dígito, L=letra mayúscula)
_STATION_ID_PATTERN = re.compile(r'^\d{2}[A-Z]{2}\d{3}$')


def validate_station_id(station_id: object) -> str:
    """Valida y normaliza un ID de estación hidrométrica.

    Normalización aplicada antes de validar el patrón:
      - strip() para quitar espacios/tabulaciones del inicio y del final
      - upper() para convertir a mayúsculas

    Retorna:
        str: El ID normalizado si cumple el patrón DD-LL-DDD.

    Lanza:
        ValueError: Si el valor es None, vacío, contiene espacios internos,
                    no tiene exactamente 7 caracteres, o no cumple el patrón
                    dígito-dígito-letra-letra-dígito-dígito-dígito.
    """
    # 1. Rechazo de None
    if station_id is None:
        raise ValueError(
            "El ID de estación no puede ser None. "
            "Se esperaba una cadena con el formato DD-LL-DDD (ej. '08MF005')."
        )

    # 2. Conversión a str por seguridad y normalización de bordes
    normalized = str(station_id).strip().upper()

    # 3. Rechazo de cadena vacía (antes y después del strip)
    if not normalized:
        raise ValueError(
            "El ID de estación no puede ser una cadena vacía. "
            "Se esperaba el formato DD-LL-DDD (ej. '08MF005')."
        )

    # 4. Rechazo de espacios internos (después del strip, si aún quedan)
    if ' ' in normalized or '\t' in normalized:
        raise ValueError(
            f"El ID de estación '{station_id}' contiene espacios o tabulaciones "
            "internas. El formato requerido es DD-LL-DDD sin espacios (ej. '08MF005')."
        )

    # 5. Rechazo de longitud incorrecta
    if len(normalized) != 7:
        raise ValueError(
            f"El ID de estación '{station_id}' tiene {len(normalized)} carácter(es) "
            "tras la normalización, pero se requieren exactamente 7 "
            "(formato DD-LL-DDD, ej. '08MF005')."
        )

    # 6. Validación del patrón DD LL DDD
    if not _STATION_ID_PATTERN.match(normalized):
        raise ValueError(
            f"El ID de estación '{station_id}' no cumple el patrón requerido: "
            "2 dígitos + 2 letras mayúsculas + 3 dígitos (ej. '08MF005'). "
            f"Valor normalizado evaluado: '{normalized}'."
        )

    return normalized
