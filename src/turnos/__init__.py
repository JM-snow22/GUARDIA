"""GUARDIA: paquete de optimización de turnos hospitalarios (Programación Entera Binaria con PuLP)."""

from .datos import Parametros
from .modelo import resolver, Resultado
from .reportes import cuadrante, validar, resumen

__all__ = ["Parametros", "resolver", "Resultado", "cuadrante", "validar", "resumen"]
__version__ = "1.0.0"
