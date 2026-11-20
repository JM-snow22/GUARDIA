@echo off
chcp 65001 >nul
title Optimizacion de turnos hospitalarios
cd /d "%~dp0"

rem ---- Buscar Python ----
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [ERROR] No se encontro Python.
    echo Instale Python 3.10 o superior desde https://www.python.org/downloads/
    echo y marque la casilla "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

rem ---- Crear entorno virtual e instalar dependencias (solo la primera vez) ----
if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    %PY% -m venv .venv
    if errorlevel 1 goto error
)
set "VPY=.venv\Scripts\python.exe"
if not exist ".venv\.instalado" (
    echo Instalando dependencias, puede tardar unos minutos la primera vez...
    "%VPY%" -m pip install --upgrade pip --quiet
    "%VPY%" -m pip install -r requirements.txt --quiet
    if errorlevel 1 goto error
    echo ok> ".venv\.instalado"
)

:menu
echo.
echo ==============================================================
echo   GUARDIA - OPTIMIZACION DE TURNOS HOSPITALARIOS
echo ==============================================================
echo   1. Ejecutar el modelo completo (main)
echo   2. Abrir la interfaz web
echo   3. Ejecutar el modulo de IA (prediccion de demanda)
echo   4. Ejecutar las pruebas automaticas
echo   5. Salir
echo.
set "op="
set /p op="Elija una opcion [1-5]: "
if "%op%"=="1" goto op1
if "%op%"=="2" goto interfaz
if "%op%"=="3" goto op3
if "%op%"=="4" goto op4
if "%op%"=="5" exit /b 0
goto menu

:op1
"%VPY%" main\main.py
echo.
echo Los resultados quedaron en la carpeta "resultados".
pause
goto menu

:op3
"%VPY%" ia\prediccion_demanda.py
pause
goto menu

:op4
"%VPY%" -m unittest discover -s tests -v
pause
goto menu

:interfaz
echo Abriendo http://localhost:8501  (cierre esta ventana o pulse Ctrl+C para detener)
start "" http://localhost:8501
"%VPY%" -m streamlit run interfaz\app.py
goto menu

:error
echo.
echo [ERROR] Fallo la instalacion. Revise su conexion a internet e intente de nuevo.
echo Si el problema continua, borre la carpeta .venv y vuelva a ejecutar este archivo.
pause
exit /b 1
