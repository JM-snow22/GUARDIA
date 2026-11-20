"""
Modelo de Programación Entera Binaria.

Variables (como exige el enunciado):
    x[k, t] ∈ {0,1}  1 si el profesional k es asignado al turno t
    y[k]    >= 0     costo acumulado del profesional k (USD)
    z[t]    ∈ Z+     personal externo planificado en el turno t

min  Σ_k y_k + Σ_t (1 + α) C_t z_t
s.a. y_k = Σ_t C_t x_kt                          ∀k   (costo acumulado)
     Σ_k x_kt + z_t >= R_t                       ∀t   (1) cobertura
     Σ_{t∈T_d} x_kt <= 1                         ∀k,d (2) un turno por día
     x_kt + x_k,t+1 <= 1                         ∀k, t noche (3) descanso post-noche
     Σ_t x_kt <= máx_turnos                      ∀k   (4) límite legal
     1 <= Σ_{t∈noches} x_kt <= 2                 ∀k   (5) equidad (opcional)
"""

from dataclasses import dataclass, field

import pulp

from .compat import variables, resolver_modelo, valor
from .datos import Parametros


@dataclass
class Resultado:
    estado: str
    params: Parametros
    total: float = 0.0
    costo_interno: float = 0.0
    costo_externo: float = 0.0
    turnos_externos: int = 0
    asignacion: dict = field(default_factory=dict)  # (k, t) -> bool
    externos: dict = field(default_factory=dict)    # t -> int

    @property
    def optimo(self):
        return self.estado == "Optimal"


def resolver(p: Parametros | None = None) -> Resultado:
    p = p or Parametros()
    K, T = p.profesionales, p.turnos

    m = pulp.LpProblem("Asignacion_Personal_Hospitalario", pulp.LpMinimize)
    x = variables(m, "x", [(k, t) for k in K for t in T], cat="Binary")
    y = variables(m, "y", K, low=0)
    z = variables(m, "z", T, cat="Integer", low=0) if p.usar_externos else None

    # Función objetivo
    obj = pulp.lpSum(y[k] for k in K)
    if p.usar_externos:
        obj = obj + pulp.lpSum((1 + p.prima_externo) * p.C(t) * z[t] for t in T)
    m += obj

    # Costo acumulado por profesional
    for k in K:
        m += y[k] == pulp.lpSum(p.C(t) * x[k, t] for t in T), f"Costo_{k}"

    # (1) Cobertura mínima
    for t in T:
        oferta = pulp.lpSum(x[k, t] for k in K)
        if p.usar_externos:
            oferta = oferta + z[t]
        m += oferta >= p.R(t), f"Cobertura_t{t}"

    for k in K:
        # (2) Un turno por día
        for d in p.dias:
            m += pulp.lpSum(x[k, t] for t in T if p.dia_de(t) == d) <= 1, f"UnTurno_{k}_d{d}"
        # (3) Descanso post-noche: noche t y mañana t+1 son consecutivos
        for t in p.noches:
            if t + 1 in T:
                m += x[k, t] + x[k, t + 1] <= 1, f"Descanso_{k}_t{t}"
        # (4) Límite de turnos en el ciclo
        m += pulp.lpSum(x[k, t] for t in T) <= p.max_turnos, f"MaxTurnos_{k}"
        # (5) Equidad de noches (criterio complementario)
        if p.equidad_noches:
            m += pulp.lpSum(x[k, t] for t in p.noches) >= 1, f"MinNoche_{k}"
            m += pulp.lpSum(x[k, t] for t in p.noches) <= 2, f"MaxNoche_{k}"

    estado = resolver_modelo(m)
    res = Resultado(estado=estado, params=p)
    if not res.optimo:
        return res

    res.asignacion = {(k, t): valor(x[k, t]) > 0.5 for k in K for t in T}
    res.externos = {t: (int(round(valor(z[t]))) if p.usar_externos else 0) for t in T}
    res.costo_interno = sum(p.C(t) for (k, t), a in res.asignacion.items() if a)
    res.costo_externo = sum((1 + p.prima_externo) * p.C(t) * n for t, n in res.externos.items())
    res.turnos_externos = sum(res.externos.values())
    res.total = res.costo_interno + res.costo_externo
    return res
