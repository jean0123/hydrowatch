"""
cooldown_validators.py
======================
Módulo autocontenido (solo stdlib, sin dependencias de Django) para validar
el intervalo de cooldown de notificaciones de alerta.

Reglas de dominio:
  - None  → devuelve el default (60 minutos).
  - int o string numérico en [1, 1440] → devuelve el entero validado.
  - Cualquier otro valor (0, negativo, no numérico, NaN, > 1440) → ValueError.
"""

import math


_DEFAULT_COOLDOWN_MINUTES = 60
_MIN_COOLDOWN_MINUTES = 1
_MAX_COOLDOWN_MINUTES = 1440  # 24 horas


def validate_cooldown_minutes(minutes):
    """Valida y devuelve el cooldown en minutos.

    Parameters
    ----------
    minutes : int | str | None
        Valor a validar.  Puede ser un entero, un string numérico (p.ej. '120')
        o None para usar el valor por defecto.

    Returns
    -------
    int
        El cooldown validado en minutos, o 60 si *minutes* es None.

    Raises
    ------
    ValueError
        Si *minutes* es cero, negativo, no numérico, NaN, o mayor que 1440.
    """
    # Caso None → default
    if minutes is None:
        return _DEFAULT_COOLDOWN_MINUTES

    # Intentar convertir a entero
    # Aceptamos int o string numérico; rechazamos float NaN/infinito y strings
    # no numéricos.
    if isinstance(minutes, float):
        if math.isnan(minutes) or math.isinf(minutes):
            raise ValueError(
                f"El cooldown debe ser un número entero válido; "
                f"se recibió: {minutes!r}"
            )
        # Permitir floats que sean valores enteros exactos (p.ej. 60.0)
        if minutes != int(minutes):
            raise ValueError(
                f"El cooldown debe ser un número entero (sin decimales); "
                f"se recibió: {minutes!r}"
            )
        value = int(minutes)
    elif isinstance(minutes, bool):
        # bool es subclase de int en Python, pero semánticamente no es válido
        raise ValueError(
            f"El cooldown debe ser un número entero, no un booleano; "
            f"se recibió: {minutes!r}"
        )
    elif isinstance(minutes, int):
        value = minutes
    elif isinstance(minutes, str):
        stripped = minutes.strip()
        if not stripped:
            raise ValueError(
                "El cooldown no puede ser una cadena vacía; "
                "se esperaba un entero entre 1 y 1440."
            )
        try:
            value = int(stripped)
        except ValueError:
            raise ValueError(
                f"El cooldown debe ser un string numérico entero; "
                f"se recibió: {minutes!r}"
            )
    else:
        raise ValueError(
            f"El cooldown debe ser un entero o string numérico; "
            f"se recibió un valor de tipo {type(minutes).__name__!r}: {minutes!r}"
        )

    # Validación de rango
    if value <= 0:
        raise ValueError(
            f"El cooldown debe ser mayor que cero; "
            f"se recibió: {value} (mínimo permitido: {_MIN_COOLDOWN_MINUTES} minuto)."
        )
    if value > _MAX_COOLDOWN_MINUTES:
        raise ValueError(
            f"El cooldown no puede superar {_MAX_COOLDOWN_MINUTES} minutos (24 horas); "
            f"se recibió: {value}."
        )

    return value
