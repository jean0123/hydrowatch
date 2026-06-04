"""
precip_validators.py
====================
Módulo autocontenido (solo stdlib) con validación de dominio para lecturas
de precipitación en milímetros.

Hallazgo F-6 — sin dependencias de Django ni de terceros.
"""

import math

# Límite físico superior reconocido mundialmente (mm/h)
_MAX_PRECIPITATION_MM = 500.0
_MIN_PRECIPITATION_MM = 0.0


def validate_precipitation_mm(value):
    """Valida y devuelve un float de precipitación en milímetros.

    Reglas:
    - value no puede ser None.
    - value debe ser numérico o un string numérico convertible a float.
    - El resultado no puede ser NaN ni infinito.
    - El resultado debe estar en el rango [0, 500] inclusive.

    Parámetros
    ----------
    value : cualquier tipo
        Lectura de precipitación candidata.

    Devuelve
    --------
    float
        El valor validado como float.

    Lanza
    -----
    ValueError
        Si value no supera cualquiera de las comprobaciones anteriores.
    """
    # 1. Rechazar None explícitamente
    if value is None:
        raise ValueError(
            "El valor de precipitación no puede ser None; se esperaba un número >= 0."
        )

    # 2. Intentar conversión a float (también acepta strings numéricos)
    try:
        converted = float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"El valor de precipitación '{value!r}' no es numérico y no puede "
            "convertirse a float."
        )

    # 3. Rechazar NaN
    if math.isnan(converted):
        raise ValueError(
            "El valor de precipitación no puede ser NaN."
        )

    # 4. Rechazar infinitos
    if math.isinf(converted):
        raise ValueError(
            "El valor de precipitación no puede ser infinito."
        )

    # 5. Rechazar negativos
    if converted < _MIN_PRECIPITATION_MM:
        raise ValueError(
            f"El valor de precipitación {converted} mm es negativo; "
            f"el mínimo permitido es {_MIN_PRECIPITATION_MM} mm."
        )

    # 6. Rechazar valores por encima del máximo físico
    if converted > _MAX_PRECIPITATION_MM:
        raise ValueError(
            f"El valor de precipitación {converted} mm supera el máximo físico "
            f"mundial permitido de {_MAX_PRECIPITATION_MM} mm."
        )

    return converted
