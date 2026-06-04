"""
filename_validators.py
======================
Módulo autocontenido (solo stdlib, sin dependencias de Django) para
validar nombres de archivo de reportes PDF antes de que lleguen al
filesystem.

Resuelve el hallazgo F-8 (path traversal / archivos corruptos).
"""

import re

# Patrón de caracteres permitidos: letras, dígitos, guiones, guiones
# bajos y puntos.  El nombre NO puede empezar por punto.
_VALID_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]*$')

# Caracteres reservados en Windows (y potencialmente problemáticos en Unix)
_RESERVED_CHARS = set('<>:"|?*')

# Longitud máxima permitida
_MAX_LENGTH = 100


def validate_report_filename(name: str) -> str:
    """Valida y devuelve *name* si es un nombre de archivo seguro.

    Reglas:
    - Debe ser un ``str`` no nulo y no vacío.
    - Máximo ``100`` caracteres.
    - Solo letras (a-z, A-Z), dígitos (0-9), guiones (``-``),
      guiones bajos (``_``) y puntos (``.``).
    - No puede empezar por punto (evita archivos ocultos / ``..``).
    - No puede contener separadores de ruta (``/`` o ``\\``).
    - No puede contener la secuencia ``..``.
    - No puede contener caracteres reservados de Windows/Unix:
      ``< > : " | ? *``.
    - No puede contener espacios.

    Parámetros
    ----------
    name:
        Nombre de archivo propuesto.

    Devuelve
    --------
    str
        El mismo *name* recibido si supera todas las validaciones.

    Lanza
    -----
    ValueError
        Con un mensaje descriptivo si alguna regla no se cumple.
    """
    # 1. Debe ser un string no-None
    if name is None:
        raise ValueError(
            "El nombre de archivo no puede ser None."
        )

    # 2. No vacío
    if not isinstance(name, str) or name == "":
        raise ValueError(
            "El nombre de archivo no puede ser una cadena vacía."
        )

    # 3. Sin separadores de ruta (detectar path traversal explícito)
    if "/" in name or "\\" in name:
        raise ValueError(
            f"El nombre de archivo contiene separadores de ruta no "
            f"permitidos ('/' o '\\'): {name!r}"
        )

    # 4. Sin la secuencia '..'
    if ".." in name:
        raise ValueError(
            f"El nombre de archivo contiene la secuencia '..' no "
            f"permitida: {name!r}"
        )

    # 5. Sin caracteres reservados de Windows/Unix
    found_reserved = _RESERVED_CHARS.intersection(name)
    if found_reserved:
        raise ValueError(
            f"El nombre de archivo contiene caracteres reservados "
            f"{sorted(found_reserved)!r}: {name!r}"
        )

    # 6. Sin espacios
    if " " in name:
        raise ValueError(
            f"El nombre de archivo no puede contener espacios: {name!r}"
        )

    # 7. Longitud máxima
    if len(name) > _MAX_LENGTH:
        raise ValueError(
            f"El nombre de archivo supera los {_MAX_LENGTH} caracteres "
            f"permitidos (longitud actual: {len(name)}): {name!r}"
        )

    # 8. Patrón general: solo caracteres permitidos y no empieza por punto
    if not _VALID_PATTERN.match(name):
        raise ValueError(
            f"El nombre de archivo contiene caracteres no permitidos o "
            f"empieza por punto: {name!r}. Solo se permiten letras, "
            f"dígitos, guiones, guiones bajos y puntos, y el nombre no "
            f"puede empezar por punto."
        )

    return name
