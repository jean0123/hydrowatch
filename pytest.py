"""Bootstrap: instala pytest real y re-lanza."""
import subprocess
import sys
import os

def main():
    # Instala pytest en el venv
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pytest", "--quiet"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Ahora usa el pytest recién instalado
    import runpy
    sys.argv[0] = "pytest"
    # Eliminar este archivo del path para que no se importe de nuevo
    this_dir = os.path.dirname(os.path.abspath(__file__))
    if this_dir in sys.path:
        sys.path.remove(this_dir)
    # Re-importar el pytest real
    runpy.run_module("pytest", run_name="__main__", alter_sys=True)

if __name__ == "__main__":
    main()

# Cuando se hace: python -m pytest, Python ejecuta pytest/__main__.py o pytest.py
# Necesitamos que esto sea un paquete para que -m pytest funcione como módulo
import subprocess, sys as _sys
result = subprocess.run(
    [_sys.executable, "-m", "pip", "install", "pytest", "--quiet"],
    capture_output=True
)
if result.returncode == 0:
    # pytest instalado, pero ya estamos en ejecución de este módulo
    # No podemos relanzar desde aquí de forma limpia
    pass
