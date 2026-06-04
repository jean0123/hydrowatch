"""
validators.py — Módulo AUTOCONTENIDO de validación para lecturas hidrométricas.
Sin dependencias de Django ni de ningún framework externo; solo stdlib Python.
"""

import math


def validate_reading(water_level_m, flow_rate_cms):
    """
    Valida una lectura hidrométrica de nivel de agua y caudal.

    Parámetros
    ----------
    water_level_m : float
        Nivel de agua en metros.
    flow_rate_cms : float
        Caudal en metros cúbicos por segundo (m³/s).

    Lanza
    -----
    ValueError
        Si alguno de los valores es NaN, negativo o supera el rango físico
        plausible definido para cada magnitud.

    Rangos válidos
    --------------
    water_level_m : [0, 100]  metros
    flow_rate_cms : [0, 50000] m³/s
    """
    # --- Validación de water_level_m ---
    try:
        wl = float(water_level_m)
    except (TypeError, ValueError):
        raise ValueError(
            f"water_level_m inválido: '{water_level_m}' no puede convertirse a número."
        )

    if math.isnan(wl):
        raise ValueError(
            "water_level_m inválido: el valor es NaN. "
            "Se requiere un número real en el rango [0, 100] m."
        )
    if wl < 0:
        raise ValueError(
            f"water_level_m inválido: {wl} es negativo. "
            "El nivel de agua no puede ser menor que 0 m."
        )
    if wl > 100:
        raise ValueError(
            f"water_level_m inválido: {wl} supera el máximo físico plausible de 100 m."
        )

    # --- Validación de flow_rate_cms ---
    try:
        fr = float(flow_rate_cms)
    except (TypeError, ValueError):
        raise ValueError(
            f"flow_rate_cms inválido: '{flow_rate_cms}' no puede convertirse a número."
        )

    if math.isnan(fr):
        raise ValueError(
            "flow_rate_cms inválido: el valor es NaN. "
            "Se requiere un número real en el rango [0, 50000] m³/s."
        )
    if fr < 0:
        raise ValueError(
            f"flow_rate_cms inválido: {fr} es negativo. "
            "El caudal no puede ser menor que 0 m³/s."
        )
    if fr > 50000:
        raise ValueError(
            f"flow_rate_cms inválido: {fr} supera el máximo físico plausible de 50 000 m³/s."
        )
