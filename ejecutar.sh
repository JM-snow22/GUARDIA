#!/usr/bin/env bash
# Ejecutar en macOS / Linux:  bash ejecutar.sh
cd "$(dirname "$0")"
PY=$(command -v python3 || command -v python)
if [ -z "$PY" ]; then echo "[ERROR] Instale Python 3.10 o superior."; exit 1; fi
if [ ! -x .venv/bin/python ]; then echo "Creando entorno virtual..."; "$PY" -m venv .venv || exit 1; fi
VPY=.venv/bin/python
if [ ! -f .venv/.instalado ]; then
  echo "Instalando dependencias (solo la primera vez)..."
  "$VPY" -m pip install --upgrade pip --quiet && "$VPY" -m pip install -r requirements.txt --quiet || exit 1
  touch .venv/.instalado
fi
while true; do
  echo
  echo "=============================================================="
  echo "  GUARDIA - OPTIMIZACION DE TURNOS HOSPITALARIOS"
  echo "=============================================================="
  echo "  1. Ejecutar el modelo completo (main)"
  echo "  2. Abrir la interfaz web"
  echo "  3. Ejecutar el modulo de IA (prediccion de demanda)"
  echo "  4. Ejecutar las pruebas automaticas"
  echo "  5. Salir"
  read -rp "Elija una opcion [1-5]: " op
  case "$op" in
    1) "$VPY" main/main.py ;;
    2) echo "Abra http://localhost:8501 (Ctrl+C para detener)"; "$VPY" -m streamlit run interfaz/app.py ;;
    3) "$VPY" ia/prediccion_demanda.py ;;
    4) "$VPY" -m unittest discover -s tests -v ;;
    5) exit 0 ;;
  esac
done
