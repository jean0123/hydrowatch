"""
rule_validators.py
------------------
Módulo AUTOCONTENIDO de validación de dominio para reglas de alerta.
Sin dependencias de Django — solo stdlib.
"""

import math
import re

ALLOWED_OPERATORS = {'gt', 'gte', 'lt', 'lte', 'eq'}

# Patrón básico: algo@algo.algo  (sin espacios, con al menos un punto en el dominio)
_EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


def validate_alert_rule(threshold, operator, email):
    """Valida los parámetros de una regla de alerta.

    Parámetros
    ----------
    threshold : numeric o str
        Valor umbral; debe ser convertible a float, no NaN ni infinito.
    operator : str
        Operador de comparación; debe pertenecer a {'gt','gte','lt','lte','eq'}.
    email : str
        Dirección de correo; debe cumplir el formato básico algo@algo.algo
        y no contener espacios.

    Devuelve
    --------
    tuple[float, str, str]
        (threshold_float, operator, email) ya validados.

    Lanza
    -----
    ValueError
        Si cualquiera de los parámetros es inválido.
    """
    # --- Validar threshold ---
    try:
        threshold_float = float(threshold)
    except (TypeError, ValueError):
        raise ValueError(
            f"El umbral (threshold) debe ser numérico; se recibió: {threshold!r}"
        )

    if math.isnan(threshold_float):
        raise ValueError(
            "El umbral (threshold) no puede ser NaN."
        )

    if math.isinf(threshold_float):
        raise ValueError(
            "El umbral (threshold) no puede ser infinito."
        )

    # --- Validar operator ---
    if operator not in ALLOWED_OPERATORS:
        raise ValueError(
            f"El operador {operator!r} no es válido. "
            f"Operadores permitidos: {sorted(ALLOWED_OPERATORS)}"
        )

    # --- Validar email ---
    if not isinstance(email, str) or not _EMAIL_RE.match(email):
        raise ValueError(
            f"El email {email!r} no tiene un formato válido (se esperaba algo@algo.algo, sin espacios)."
        )

    return (threshold_float, operator, email)
