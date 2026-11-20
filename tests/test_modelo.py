"""
Pruebas automáticas del modelo.

    python -m unittest discover -s tests -v
"""

import sys
import unittest
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ))

from turnos import Parametros, resolver, validar


class TestModelo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Parametros()
        cls.a = resolver(cls.base)

    def test_enunciado_original_es_infactible(self):
        r = resolver(replace(self.base, usar_externos=False))
        self.assertEqual(r.estado, "Infeasible")

    def test_escenario_legal_optimo(self):
        self.assertTrue(self.a.optimo)
        self.assertAlmostEqual(self.a.total, 6380)
        self.assertEqual(self.a.turnos_externos, 8)

    def test_solucion_cumple_restricciones(self):
        self.assertEqual(validar(self.a), [])

    def test_maximo_cuatro_turnos(self):
        for k in self.base.profesionales:
            self.assertLessEqual(sum(self.a.asignacion[k, t] for t in self.base.turnos), 4)

    def test_escenario_cinco_turnos(self):
        r = resolver(replace(self.base, max_turnos=5, usar_externos=False))
        self.assertAlmostEqual(r.total, 5900)

    def test_noche_mas_diez_por_ciento(self):
        r = resolver(replace(self.base, costo_tipo={1: 120, 2: 140, 3: 220}))
        self.assertAlmostEqual(r.total, 6580)

    def test_prediccion_ia_respeta_minimos(self):
        from ia.prediccion_demanda import cobertura_predicha, MINIMOS
        R, detalle, _ = cobertura_predicha()
        self.assertEqual(len(R), 15)
        for t, req in R.items():
            self.assertGreaterEqual(req, MINIMOS[(t - 1) % 3 + 1])


if __name__ == "__main__":
    unittest.main()
