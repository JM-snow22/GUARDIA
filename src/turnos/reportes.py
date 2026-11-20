"""Cuadrante en Pandas, validaciones independientes y resumen de resultados."""

import pandas as pd

from .datos import COSTO_ACTUAL
from .modelo import Resultado


def cuadrante(res: Resultado) -> pd.DataFrame:
    p, A = res.params, res.asignacion
    filas = []
    for k in p.profesionales:
        fila = {"Profesional": k}
        for d in p.dias:
            fila[f"Día {d}"] = next(
                (p.etiqueta(t) for t in p.turnos if p.dia_de(t) == d and A[k, t]), "Descanso")
        fila["Turnos"] = sum(A[k, t] for t in p.turnos)
        fila["Noches"] = sum(A[k, t] for t in p.noches)
        fila["Costo (USD)"] = int(sum(p.C(t) for t in p.turnos if A[k, t]))
        filas.append(fila)
    if p.usar_externos:
        fila = {"Profesional": "Externos"}
        for d in p.dias:
            n = sum(res.externos[t] for t in p.turnos if p.dia_de(t) == d)
            fila[f"Día {d}"] = f"{n} externo(s)" if n else "-"
        fila["Turnos"] = res.turnos_externos
        fila["Noches"] = sum(res.externos[t] for t in p.noches)
        fila["Costo (USD)"] = int(round(res.costo_externo))
        filas.append(fila)
    return pd.DataFrame(filas)


def validar(res: Resultado) -> list[str]:
    """Comprueba la solución sin usar el solver. Devuelve la lista de errores (vacía si todo cumple)."""
    p, A, E = res.params, res.asignacion, res.externos
    errores = []
    for t in p.turnos:
        if sum(A[k, t] for k in p.profesionales) + E.get(t, 0) < p.R(t):
            errores.append(f"Cobertura insuficiente en t{t}")
    for k in p.profesionales:
        for d in p.dias:
            if sum(A[k, t] for t in p.turnos if p.dia_de(t) == d) > 1:
                errores.append(f"{k} tiene más de un turno el día {d}")
        for t in p.noches:
            if t + 1 in p.turnos and A[k, t] and A[k, t + 1]:
                errores.append(f"{k} trabaja la mañana t{t + 1} después de la noche t{t}")
        if sum(A[k, t] for t in p.turnos) > p.max_turnos:
            errores.append(f"{k} supera el máximo de {p.max_turnos} turnos")
    return errores


def resumen(res: Resultado) -> dict:
    ahorro = COSTO_ACTUAL - res.total
    return {
        "Estado": res.estado,
        "Costo interno (USD)": round(res.costo_interno),
        "Costo externo (USD)": round(res.costo_externo),
        "Turnos externos": res.turnos_externos,
        "Costo total (USD)": round(res.total),
        "Ahorro vs. actual (USD)": round(ahorro),
        "Ahorro (%)": round(100 * ahorro / COSTO_ACTUAL, 1),
    }
