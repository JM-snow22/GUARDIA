"""
EJECUTAR DESDE VISUAL STUDIO CODE: abra este archivo y pulse el botón ▶ (Run Python File).

Instala lo que falte con el mismo Python que usa VS Code y muestra un menú:
  1. Modelo completo   2. Interfaz web   3. Módulo de IA   4. Pruebas
También acepta la opción como argumento:  python run.py 1
"""

import importlib.util
import subprocess
import sys
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PY = sys.executable


def instalar():
    faltan = [m for m in ("pulp", "pandas", "numpy", "matplotlib", "streamlit")
              if importlib.util.find_spec(m) is None]
    pulp_nuevo = False
    if "pulp" not in faltan:
        import pulp
        pulp_nuevo = not hasattr(pulp.LpVariable, "dicts")
    if faltan or pulp_nuevo:
        print("Instalando dependencias (solo la primera vez)...")
        subprocess.check_call([PY, "-m", "pip", "install", "-r", str(RAIZ / "requirements.txt")])


def correr(*args):
    subprocess.call([PY, *args], cwd=RAIZ)


def main():
    instalar()
    op = sys.argv[1] if len(sys.argv) > 1 else None
    while True:
        if op is None:
            print("\n" + "=" * 60)
            print("  GUARDIA - OPTIMIZACIÓN DE TURNOS HOSPITALARIOS")
            print("=" * 60)
            print("  1. Ejecutar el modelo completo")
            print("  2. Abrir la interfaz web")
            print("  3. Ejecutar el módulo de IA")
            print("  4. Ejecutar las pruebas")
            print("  5. Salir")
            op = input("Opción [1-5]: ").strip()
        if op == "1":
            correr("main/main.py")
        elif op == "2":
            print("Abriendo http://localhost:8501  (Ctrl+C en la terminal para detener)")
            webbrowser.open("http://localhost:8501")
            correr("-m", "streamlit", "run", "interfaz/app.py")
        elif op == "3":
            correr("ia/prediccion_demanda.py")
        elif op == "4":
            correr("-m", "unittest", "discover", "-s", "tests", "-v")
        elif op == "5":
            break
        if len(sys.argv) > 1:
            break
        op = None


if __name__ == "__main__":
    main()
