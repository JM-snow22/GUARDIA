"""
GUARDIA - Gestión Unificada de Asignación de Recursos y Demanda con Inteligencia Artificial

Programa principal: resuelve todos los escenarios y guarda los resultados.

    python main/main.py

Genera en la carpeta resultados/:
    cuadrante_optimo_turnos.csv   cuadrante del escenario legal (A)
    cuadrante_escenario_B.csv     cuadrante con máximo 5 turnos (comparación)
    sensibilidad.csv              análisis de sensibilidad
    comparacion_costos.png        gráfica de costos
    sensibilidad.png              gráfica de sensibilidad
"""

import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from turnos import Parametros, resolver, cuadrante, validar, resumen
from turnos.compat import nombre_solver
from turnos.datos import COSTO_ACTUAL

SALIDA = RAIZ / "resultados"
SALIDA.mkdir(exist_ok=True)
pd.set_option("display.width", 160)


def titulo(texto):
    print("\n" + "=" * 70 + f"\n{texto}\n" + "=" * 70)


def comprobar(res, nombre):
    errores = validar(res)
    if errores:
        raise AssertionError(f"{nombre}: " + "; ".join(errores))


def main():
    titulo(f"GUARDIA - ASIGNACIÓN ÓPTIMA DE PERSONAL HOSPITALARIO  |  solver: {nombre_solver()}")
    base = Parametros()

    # 0. Enunciado original: máximo 4 turnos y sin externos
    orig = resolver(replace(base, usar_externos=False))
    print(f"\nEnunciado original (máx. 4 turnos, sin externos): {orig.estado}")
    print("  -> Se requieren 40 asignaciones y la capacidad es 8 x 4 = 32.")

    # A. Escenario legal
    a = resolver(base)
    comprobar(a, "Escenario A")
    titulo("ESCENARIO A - Legal (máx. 4 turnos + externos planificados)")
    for k, v in resumen(a).items():
        print(f"  {k:<26}{v}")
    cua = cuadrante(a)
    print("\n" + cua.to_string(index=False))
    cua.to_csv(SALIDA / "cuadrante_optimo_turnos.csv", index=False, encoding="utf-8-sig")

    # B. Comparación: máximo 5 turnos
    b = resolver(replace(base, max_turnos=5, usar_externos=False))
    comprobar(b, "Escenario B")
    titulo("ESCENARIO B - Comparación (máx. 5 turnos, sin externos)")
    for k, v in resumen(b).items():
        print(f"  {k:<26}{v}")
    cuadrante(b).to_csv(SALIDA / "cuadrante_escenario_B.csv", index=False, encoding="utf-8-sig")

    # Respuesta a la pregunta 2
    minimo = 5900
    titulo("PREGUNTA 2 - Sobrecosto por reemplazos")
    print(f"  Sobrecosto actual sobre el mínimo (${minimo:,}):     ${COSTO_ACTUAL - minimo:,}")
    print(f"  Sobrecosto optimizado sobre el mínimo:           ${a.total - minimo:,.0f}")
    print(f"  Reducción del sobrecosto:                        "
          f"{100 * (1 - (a.total - minimo) / (COSTO_ACTUAL - minimo)):.1f} %")

    # Análisis de sensibilidad
    casos = [
        ("Base", base),
        ("Noche +10 % ($220)", replace(base, costo_tipo={1: 120, 2: 140, 3: 220})),
        ("Todas las tarifas +10 %", replace(base, costo_tipo={1: 132, 2: 154, 3: 220})),
        ("Prima externa 25 %", replace(base, prima_externo=0.25)),
        ("Prima externa 100 %", replace(base, prima_externo=1.00)),
        ("Ausencia de 1 profesional (7)", replace(base, n_profesionales=7)),
        ("Cobertura noche = 3", replace(base, cobertura_tipo={1: 3, 2: 3, 3: 3})),
    ]
    filas = []
    for nombre, p in casos:
        r = resolver(p)
        filas.append({"Escenario": nombre, "Estado": r.estado,
                      "Costo total (USD)": round(r.total), "Turnos externos": r.turnos_externos})
    sens = pd.DataFrame(filas)
    titulo("ANÁLISIS DE SENSIBILIDAD (Escenario A)")
    print(sens.to_string(index=False))
    sens.to_csv(SALIDA / "sensibilidad.csv", index=False, encoding="utf-8-sig")

    # Escenario con cobertura predicha por la IA
    try:
        from ia.prediccion_demanda import cobertura_predicha
        R, detalle, met = cobertura_predicha()
        ia = resolver(replace(base, cobertura_por_turno=R))
        titulo("ESCENARIO IA - Cobertura ajustada por predicción de demanda")
        print(f"  Modelo de demanda: MAE = {met['MAE']:.2f} pacientes, R² = {met['R2']:.3f}")
        print(f"  Cobertura requerida total: {sum(R.values())} asignaciones (base: 40)")
        print(f"  Estado: {ia.estado} | Costo total: ${ia.total:,.0f} | Externos: {ia.turnos_externos}")
        detalle.to_csv(SALIDA / "cobertura_predicha_ia.csv", index=False, encoding="utf-8-sig")
    except Exception as e:  # el programa principal no depende del módulo de IA
        print(f"\n(Módulo de IA omitido: {e})")

    graficas(a, b, sens)
    titulo("VALIDACIONES COMPLETADAS")
    print("  Cobertura, un turno por día, descanso post-noche y límite de turnos: OK")
    print(f"  Resultados guardados en: {SALIDA}")


def graficas(a, b, sens):
    az, azc, gr = "#1F4E79", "#7FA7CF", "#9AA3AD"
    fig, ax = plt.subplots(figsize=(8, 4.6), dpi=150)
    ax.bar("Actual", COSTO_ACTUAL, color=gr, width=.55)
    ax.bar("Escenario A\n(legal)", a.costo_interno, color=az, width=.55, label="Personal interno")
    ax.bar("Escenario A\n(legal)", a.costo_externo, bottom=a.costo_interno, color=azc, width=.55,
           label="Externos planificados")
    ax.bar("Escenario B\n(5 turnos)", b.total, color=az, width=.55)
    for i, v in enumerate([COSTO_ACTUAL, a.total, b.total]):
        ax.text(i, v + 200, f"${v:,.0f}", ha="center", fontweight="bold")
    ax.set_ylabel("USD por ciclo"); ax.set_ylim(0, COSTO_ACTUAL * 1.12)
    ax.set_title("Costo por ciclo: actual vs. optimizado", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False); ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(SALIDA / "comparacion_costos.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.4), dpi=150)
    ax.barh(sens["Escenario"][::-1], sens["Costo total (USD)"][::-1], color=azc)
    ax.set_xlabel("Costo total por ciclo (USD)")
    ax.set_title("Análisis de sensibilidad", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(SALIDA / "sensibilidad.png"); plt.close(fig)


if __name__ == "__main__":
    main()
