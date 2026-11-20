"""
Datos de entrada del problema (enunciado del Ejercicio 2).

Numeración de turnos: t = 3(d - 1) + s
    d = día (1..5), s = tipo de turno (1 Mañana, 2 Tarde, 3 Noche)
    Día 1: t1 t2 t3 | Día 2: t4 t5 t6 | ... | Día 5: t13 t14 t15
"""

from dataclasses import dataclass, field

TIPOS = {1: "Mañana", 2: "Tarde", 3: "Noche"}
COSTO_ACTUAL = 11_800  # USD por ciclo en el escenario sin optimizar


@dataclass
class Parametros:
    n_profesionales: int = 8
    n_dias: int = 5
    costo_tipo: dict = field(default_factory=lambda: {1: 120, 2: 140, 3: 200})
    cobertura_tipo: dict = field(default_factory=lambda: {1: 3, 2: 3, 3: 2})
    max_turnos: int = 4             # límite legal del enunciado
    usar_externos: bool = True      # cubrir la brecha con personal externo planificado
    prima_externo: float = 0.50     # supuesto: el externo cuesta 50 % más
    equidad_noches: bool = True     # criterio complementario: 1 a 2 noches por persona
    cobertura_por_turno: dict | None = None  # opcional: R_t por turno (p. ej. desde la IA)

    # ----- conjuntos derivados
    @property
    def profesionales(self):
        return [f"k{i}" for i in range(1, self.n_profesionales + 1)]

    @property
    def dias(self):
        return list(range(1, self.n_dias + 1))

    @property
    def turnos(self):
        return list(range(1, 3 * self.n_dias + 1))

    @staticmethod
    def dia_de(t):
        return (t - 1) // 3 + 1

    @staticmethod
    def tipo_de(t):
        return (t - 1) % 3 + 1

    @property
    def noches(self):
        return [t for t in self.turnos if self.tipo_de(t) == 3]

    def C(self, t):
        """Costo del turno t (USD)."""
        return self.costo_tipo[self.tipo_de(t)]

    def R(self, t):
        """Cobertura mínima del turno t."""
        if self.cobertura_por_turno and t in self.cobertura_por_turno:
            return int(self.cobertura_por_turno[t])
        return self.cobertura_tipo[self.tipo_de(t)]

    def etiqueta(self, t):
        return f"t{t} ({TIPOS[self.tipo_de(t)]})"
