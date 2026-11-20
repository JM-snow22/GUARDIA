"""
Módulo de IA: predicción de la demanda de pacientes en urgencias.

Entrena un modelo de regresión lineal múltiple (mínimos cuadrados, NumPy) con el
histórico de ingresos por turno y estima los pacientes esperados en el próximo ciclo.
La predicción se convierte en la cobertura requerida R_t que recibe el modelo de PuLP:

    R_t = max(cobertura mínima del enunciado, ceil(pacientes_t / pacientes_por_profesional))

Variables explicativas: tipo de turno, día de la semana, festivo y temporada de lluvias.
El histórico incluido (datos/historico_urgencias.csv) es SIMULADO con fines académicos;
en un hospital real se reemplaza por los registros de admisiones.

Uso:  python ia/prediccion_demanda.py
"""

import math
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
HISTORICO = RAIZ / "datos" / "historico_urgencias.csv"
PACIENTES_POR_PROFESIONAL = 8   # capacidad de atención por profesional y turno
MINIMOS = {1: 3, 2: 3, 3: 2}    # cobertura mínima del enunciado (Mañana, Tarde, Noche)


# ------------------------------------------------------------------ datos
def generar_historico(semanas=52, semilla=7) -> pd.DataFrame:
    """Histórico simulado de pacientes por turno (un año)."""
    rng = np.random.default_rng(semilla)
    base = {1: 20, 2: 22, 3: 13}                      # pacientes promedio por turno
    efecto_dia = [1.15, 1.0, 0.95, 0.95, 1.05, 1.2, 1.25]  # lun..dom
    filas = []
    fecha = pd.Timestamp("2025-11-03")                # lunes
    for i in range(semanas * 7):
        f = fecha + pd.Timedelta(days=i)
        festivo = int(rng.random() < 0.05)
        lluvias = int(f.month in (4, 5, 10, 11))
        for s in (1, 2, 3):
            media = base[s] * efecto_dia[f.dayofweek] * (1 + 0.20 * festivo) * (1 + 0.15 * lluvias)
            filas.append({"fecha": f.date(), "dia_semana": f.dayofweek, "turno": s,
                          "festivo": festivo, "lluvias": lluvias,
                          "pacientes": int(rng.poisson(media))})
    return pd.DataFrame(filas)


def cargar_historico() -> pd.DataFrame:
    if not HISTORICO.exists():
        HISTORICO.parent.mkdir(parents=True, exist_ok=True)
        generar_historico().to_csv(HISTORICO, index=False)
    return pd.read_csv(HISTORICO)


# ------------------------------------------------------------------ modelo
def _matriz(df: pd.DataFrame) -> np.ndarray:
    cols = [np.ones(len(df))]
    cols += [(df["turno"] == s).astype(float) for s in (2, 3)]
    cols += [(df["dia_semana"] == d).astype(float) for d in range(1, 7)]
    cols += [df["festivo"].astype(float), df["lluvias"].astype(float)]
    return np.column_stack(cols)


class PredictorDemanda:
    def __init__(self):
        self.coef = None
        self.metricas = {}

    def entrenar(self, df: pd.DataFrame):
        df = df.sort_values(["fecha", "turno"]).reset_index(drop=True)
        corte = int(len(df) * 0.8)                       # 80 % entrenamiento, 20 % prueba
        tr, te = df.iloc[:corte], df.iloc[corte:]
        self.coef, *_ = np.linalg.lstsq(_matriz(tr), tr["pacientes"].to_numpy(float), rcond=None)
        pred = _matriz(te) @ self.coef
        real = te["pacientes"].to_numpy(float)
        self.metricas = {
            "MAE": float(np.mean(np.abs(real - pred))),
            "R2": float(1 - np.sum((real - pred) ** 2) / np.sum((real - real.mean()) ** 2)),
        }
        return self

    def predecir(self, escenario: pd.DataFrame) -> np.ndarray:
        return np.maximum(_matriz(escenario) @ self.coef, 0)


def escenario_ciclo(dia_inicio=0, festivos=(), lluvias=1, n_dias=5) -> pd.DataFrame:
    """Turnos del próximo ciclo. dia_inicio: 0 = lunes. festivos: días del ciclo (1..n) festivos."""
    filas = []
    for d in range(1, n_dias + 1):
        for s in (1, 2, 3):
            filas.append({"dia": d, "turno": s, "t": 3 * (d - 1) + s,
                          "dia_semana": (dia_inicio + d - 1) % 7,
                          "festivo": int(d in festivos), "lluvias": lluvias})
    return pd.DataFrame(filas)


def cobertura_predicha(dia_inicio=0, festivos=(), lluvias=1, n_dias=5,
                       pacientes_por_profesional=PACIENTES_POR_PROFESIONAL):
    """Entrena, predice y devuelve (dict R_t, DataFrame con el detalle, métricas)."""
    pred = PredictorDemanda().entrenar(cargar_historico())
    esc = escenario_ciclo(dia_inicio, festivos, lluvias, n_dias)
    esc["pacientes_estimados"] = pred.predecir(esc).round(1)
    esc["R_t"] = [max(MINIMOS[s], math.ceil(p / pacientes_por_profesional))
                  for s, p in zip(esc["turno"], esc["pacientes_estimados"])]
    return dict(zip(esc["t"], esc["R_t"])), esc, pred.metricas


if __name__ == "__main__":
    R, detalle, met = cobertura_predicha(dia_inicio=0, festivos=(), lluvias=1)
    print("Módulo de IA - Predicción de demanda")
    print(f"Error medio absoluto (prueba): {met['MAE']:.2f} pacientes | R²: {met['R2']:.3f}")
    print(detalle[["dia", "turno", "t", "pacientes_estimados", "R_t"]].to_string(index=False))
    salida = RAIZ / "resultados" / "cobertura_predicha_ia.csv"
    salida.parent.mkdir(exist_ok=True)
    detalle.to_csv(salida, index=False, encoding="utf-8-sig")
    print(f"\nGuardado en {salida.relative_to(RAIZ)}")
