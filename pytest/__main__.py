"""Bootstrap pytest: instala el paquete real y ejecuta."""
import subprocess
import sys
import os

# Intentar instalar pytest en el directorio del usuario
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "pytest", "--user", "--quiet"],
    capture_output=True, text=True
)

if result.returncode != 0:
    # Intentar instalar en un directorio temporal
    import tempfile
    tmpdir = tempfile.mkdtemp()
    result2 = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", f"--target={tmpdir}", "--quiet"],
        capture_output=True, text=True
    )
    if result2.returncode == 0:
        sys.path.insert(0, tmpdir)
    else:
        print("ERROR instalando pytest:", result2.stderr, file=sys.stderr)
        sys.exit(1)
else:
    # Agregar site-packages del usuario al path
    import site
    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.insert(0, user_site)

# Limpiar cache de módulos para que tome el recién instalado
for key in list(sys.modules.keys()):
    if key == "pytest" or key.startswith("pytest.") or key.startswith("_pytest"):
        del sys.modules[key]

# Eliminar el directorio actual del path para no causar conflicto
workdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if workdir in sys.path:
    sys.path.remove(workdir)

import runpy
runpy.run_module("pytest", run_name="__main__", alter_sys=True)
