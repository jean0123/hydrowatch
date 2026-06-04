"""
test_filename_validators.py
===========================
Tests pytest para el módulo filename_validators.
Solo usa stdlib + pytest (sin dependencias de Django).

Cubre el hallazgo F-8 (security): validación de nombres de archivo PDF.
"""

import pytest

from django_app.reports.filename_validators import validate_report_filename


# ---------------------------------------------------------------------------
# Casos VÁLIDOS — la función debe devolver el mismo nombre sin lanzar nada
# ---------------------------------------------------------------------------

class TestValidFilenames:
    """Nombres de archivo que deben pasar la validación."""

    def test_reporte_con_id_estacion(self):
        name = "reporte_08MF005.pdf"
        assert validate_report_filename(name) == name

    def test_informe_con_guion_y_anio(self):
        name = "informe-2026.pdf"
        assert validate_report_filename(name) == name

    def test_solo_letras(self):
        name = "reporte"
        assert validate_report_filename(name) == name

    def test_solo_digitos(self):
        name = "20260101"
        assert validate_report_filename(name) == name

    def test_exactamente_100_caracteres(self):
        name = "a" * 100
        assert validate_report_filename(name) == name

    def test_combinacion_permitida(self):
        name = "Station_A1-report.2026.pdf"
        assert validate_report_filename(name) == name

    def test_empieza_por_letra_mayuscula(self):
        name = "Reporte_Final.pdf"
        assert validate_report_filename(name) == name

    def test_empieza_por_digito(self):
        name = "2026_reporte.pdf"
        assert validate_report_filename(name) == name


# ---------------------------------------------------------------------------
# Casos INVÁLIDOS — la función debe lanzar ValueError
# ---------------------------------------------------------------------------

class TestInvalidFilenames:
    """Nombres de archivo que deben lanzar ValueError."""

    def test_none_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename(None)

    def test_cadena_vacia_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("")

    def test_path_traversal_doble_punto_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("../etc/passwd")

    def test_separador_slash_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("a/b.pdf")

    def test_caracter_reservado_menor_que_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("con<.pdf")

    def test_empieza_por_punto_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename(".oculto")

    def test_mas_de_100_caracteres_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("a" * 101)

    def test_espacio_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("con espacio.pdf")

    # --- casos adicionales de robustez ---

    def test_separador_backslash_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("a\\b.pdf")

    def test_caracter_mayor_que_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("con>.pdf")

    def test_caracter_dos_puntos_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("con:.pdf")

    def test_caracter_comilla_doble_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename('con".pdf')

    def test_caracter_pipe_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("con|.pdf")

    def test_caracter_interrogacion_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("con?.pdf")

    def test_caracter_asterisco_lanza_value_error(self):
        with pytest.raises(ValueError):
            validate_report_filename("con*.pdf")

    def test_doble_punto_sin_slash_lanza_value_error(self):
        """Secuencia '..' sin separadores también debe rechazarse."""
        with pytest.raises(ValueError):
            validate_report_filename("reporte..pdf")

    def test_mensaje_error_informativo_para_none(self):
        with pytest.raises(ValueError, match="None"):
            validate_report_filename(None)

    def test_mensaje_error_informativo_para_vacio(self):
        with pytest.raises(ValueError, match="vacía|vac"):
            validate_report_filename("")

    def test_mensaje_error_informativo_para_largo(self):
        with pytest.raises(ValueError, match="100"):
            validate_report_filename("a" * 101)
