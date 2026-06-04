"""
range_validators.py
-------------------
Módulo AUTOCONTENIDO (solo stdlib, sin Django) para validar rangos temporales
expresados en horas para las consultas del dashboard.

Rangos canónicos soportados:
  24h   → 1 día
  168h  → 7 días
  720h  → 30 días
  2160h → 90 días  (límite máximo)
"""

import math

MIN_HOURS = 1
MAX_HOURS = 2160  # 90 días


def validate_range_hours(hours):
    """
    Valida y devuelve el valor de *hours* como entero si es válido.

    Parámetros
    ----------
    hours : int | str | cualquier tipo
        Número de horas a validar.  Se aceptan strings numéricos enteros
        (p. ej. ``'24'``).

    Retorna
    -------
    int
        El valor validado convertido a entero.

    Lanza
    -----
    ValueError
        Si el valor es None, no numérico, NaN, no entero (p. ej. ``3.7``),
        menor que 1 (cero o negativo) o mayor que 2160.
    """

    # 1. Rechazar None explícitamente
    if hours is None:
        raise ValueError(
            "El parámetro 'hours' no puede ser None. "
            f"Proporcione un entero entre {MIN_HOURS} y {MAX_HOURS}."
        )

    # 2. Convertir strings numéricos
    if isinstance(hours, str):
        stripped = hours.strip()
        if not stripped:
            raise ValueError(
                "El parámetro 'hours' no puede ser una cadena vacía. "
                f"Proporcione un entero entre {MIN_HOURS} y {MAX_HOURS}."
            )
        try:
            # Sólo aceptamos representaciones de enteros (sin punto decimal)
            converted = int(stripped)
            # Asegurarse de que el string no era un float (p. ej. "3.7")
            if '.' in stripped:
                raise ValueError(
                    f"El parámetro 'hours' debe ser un número entero, "
                    f"no un valor decimal: '{hours}'."
                )
            hours = converted
        except ValueError as exc:
            raise ValueError(
                f"El parámetro 'hours' no es numérico: '{hours}'. "
                f"Proporcione un entero entre {MIN_HOURS} y {MAX_HOURS}."
            ) from exc

    # 3. Rechazar floats (incluyendo NaN e Infinity) — sólo se permiten int
    if isinstance(hours, float):
        if math.isnan(hours):
            raise ValueError(
                "El parámetro 'hours' no puede ser NaN. "
                f"Proporcione un entero entre {MIN_HOURS} y {MAX_HOURS}."
            )
        if math.isinf(hours):
            raise ValueError(
                "El parámetro 'hours' no puede ser infinito. "
                f"Proporcione un entero entre {MIN_HOURS} y {MAX_HOURS}."
            )
        raise ValueError(
            f"El parámetro 'hours' debe ser un número entero, "
            f"no un float: {hours}. "
            f"Proporcione un entero entre {MIN_HOURS} y {MAX_HOURS}."
        )

    # 4. Rechazar cualquier tipo no entero restante
    if not isinstance(hours, int):
        raise ValueError(
            f"El parámetro 'hours' tiene un tipo no válido ({type(hours).__name__}). "
            f"Proporcione un entero entre {MIN_HOURS} y {MAX_HOURS}."
        )

    # 5. Validar rango
    if hours < MIN_HOURS:
        raise ValueError(
            f"El parámetro 'hours' debe ser al menos {MIN_HOURS} (recibido: {hours}). "
            "Los valores cero o negativos no están permitidos."
        )

    if hours > MAX_HOURS:
        raise ValueError(
            f"El parámetro 'hours' excede el máximo permitido de {MAX_HOURS} horas "
            f"(90 días). Valor recibido: {hours}."
        )

    return hours
