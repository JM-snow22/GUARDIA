# GUARDIA

**Gestión Unificada de Asignación de Recursos y Demanda con Inteligencia Artificial**

Asignación óptima de personal hospitalario con PuLP + IA.

Repositorio: https://github.com/JM-snow22/GUARDIA

Modelo de **Programación Entera Binaria** en Python (PuLP) que asigna 8 profesionales de urgencias a 15 turnos (3 diarios × 5 días) al menor costo. El modelo respeta la cobertura mínima, un turno por día, el descanso después de una noche y el máximo legal de 4 turnos por profesional. Incluye un **módulo de IA** de predicción de demanda y una **interfaz web** en Streamlit.

Asignatura: Investigación de Operaciones + Desarrollo Tecnológico + IA · Ingeniería de Sistemas.

## Cómo ejecutarlo

**Requisito:** Python 3.10 o superior ([python.org](https://www.python.org/downloads/)). En Windows, marque **"Add Python to PATH"** al instalarlo.

| Sistema | Qué hacer |
|---|---|
| Windows | Doble clic en **`ejecutar.bat`** |
| macOS / Linux | `bash ejecutar.sh` |

La primera vez el script crea un entorno virtual (`.venv`) e instala las dependencias. Tarda unos minutos y necesita internet. Después aparece un menú:

```
1. Ejecutar el modelo completo (main)
2. Abrir la interfaz web          -> http://localhost:8501
3. Ejecutar el módulo de IA
4. Ejecutar las pruebas automáticas
```

Ejecución manual (alternativa):

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python main/main.py
streamlit run interfaz/app.py
python -m unittest discover -s tests -v
```

## Publicarlo como página web (Streamlit Community Cloud, gratis)

1. Entre a https://share.streamlit.io e inicie sesión con la cuenta de GitHub dueña del repositorio.
2. Pulse **Create app** → **Deploy a public app from GitHub**.
3. Repositorio: `JM-snow22/GUARDIA` · Rama: `main` · Archivo principal: `interfaz/app.py`.
4. Pulse **Deploy**. En unos minutos queda una dirección pública del tipo `https://guardia.streamlit.app`.

## Estructura del proyecto

```
optimizacion-turnos-hospitalarios/
├── main/
│   └── main.py                 Programa principal: todos los escenarios + resultados
├── src/turnos/                 Núcleo del modelo (paquete Python)
│   ├── datos.py                Parámetros del enunciado (costos, cobertura, límites)
│   ├── modelo.py               Modelo PEB: variables x_kt, y_k, z_t y restricciones
│   ├── reportes.py             Cuadrante en Pandas, validaciones y resumen
│   └── compat.py               Compatibilidad entre versiones de PuLP y solvers
├── ia/
│   └── prediccion_demanda.py   Regresión para predecir pacientes y ajustar R_t
├── interfaz/
│   └── app.py                  Interfaz web en Streamlit
├── tests/
│   └── test_modelo.py          7 pruebas automáticas
├── datos/                      Histórico de demanda (se genera solo si no existe)
├── resultados/                 CSV y gráficas generadas por main.py
├── docs/                       Documento final del trabajo
├── requirements.txt
├── ejecutar.bat / ejecutar.sh  Lanzadores con menú
└── README.md
```

## Modelo matemático

- `x[k,t] ∈ {0,1}`: 1 si el profesional *k* trabaja el turno *t* (t = 3(d − 1) + s).
- `y[k] ≥ 0`: costo acumulado del profesional *k*.
- `z[t] ∈ ℤ⁺`: personal externo planificado en el turno *t*.

**min** Σ y_k + Σ (1 + α)·C_t·z_t, sujeto a cobertura, un turno por día, descanso post-noche (x_kt + x_k,t+1 ≤ 1 en las noches), máximo 4 turnos y 1 a 2 noches por profesional.

El enunciado original es **infactible**: pide 40 asignaciones y solo hay 8 × 4 = 32. Por eso los 8 turnos faltantes se cubren con externos planificados, con un recargo supuesto del 50 %.

## Resultados principales

| Escenario | Costo por ciclo | Ahorro |
|---|---|---|
| Actual (sin optimizar) | $11.800 | — |
| **A. Legal (4 turnos + 8 externos)** | **$6.380** | **$5.420 (45,9 %)** |
| B. Comparación (5 turnos) | $5.900 | $5.900 (50,0 %) |

El sobrecosto por reemplazos frente al mínimo de $5.900 baja de $5.900 a $480 (−91,9 %).

## Problemas frecuentes

- **"No se encontró Python"**: instale Python y marque *Add Python to PATH*.
- **Falló la instalación**: borre la carpeta `.venv` y vuelva a ejecutar `ejecutar.bat`.
- **PuLP 3 o 4 instalado globalmente**: el proyecto usa su propio entorno con PuLP 2.9. Si aun así usa una versión nueva, `compat.py` cambia automáticamente al solver HiGHS (`pip install highspy`).
