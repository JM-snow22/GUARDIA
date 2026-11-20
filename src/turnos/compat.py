"""
Capa de compatibilidad entre versiones de PuLP.

- PuLP 2.x: crea variables con LpVariable.dicts y trae el solver CBC incluido.
- PuLP 3.x/4.x: las variables se crean desde el problema (add_variable_dict) y el
  solver CBC ya no viene incluido; se usa HiGHS (paquete highspy) si está instalado.

Así el proyecto funciona con la versión fijada en requirements.txt y también si el
equipo tiene instalada una versión más reciente de PuLP.
"""

import pulp


def variables(modelo, nombre, indices, cat="Continuous", low=None):
    """Diccionario de variables de decisión, independiente de la versión de PuLP."""
    indices = list(indices)
    if hasattr(pulp.LpVariable, "dicts"):                       # PuLP 2.x
        return pulp.LpVariable.dicts(nombre, indices, lowBound=low, cat=cat)
    # PuLP 3+/4: las variables se registran en el problema, una por índice
    def etiqueta(i):
        partes = i if isinstance(i, tuple) else (i,)
        return nombre + "_" + "_".join(str(v) for v in partes)
    return {i: modelo.add_variable(etiqueta(i), lowBound=low, cat=cat) for i in indices}


def _solver():
    """Primer solver disponible: CBC (incluido en PuLP 2.x) o HiGHS."""
    for nombre in ("PULP_CBC_CMD", "HiGHS", "HiGHS_CMD"):
        clase = getattr(pulp, nombre, None)
        if clase is None:
            continue
        try:
            s = clase(msg=False)
            if s.available():
                return s
        except Exception:
            continue
    raise RuntimeError(
        "No se encontró un solver disponible para PuLP.\n"
        "Solución: ejecute  pip install -r requirements.txt  (instala PuLP 2.9 con CBC),\n"
        "o bien  pip install highspy  si usa PuLP 3 o superior."
    )


def resolver_modelo(modelo):
    """Resuelve el modelo y devuelve el estado como texto ('Optimal', 'Infeasible', ...)."""
    salida = modelo.solve(_solver())
    if hasattr(pulp, "LpStatus"):                       # PuLP 2.x
        return pulp.LpStatus[modelo.status]
    codigo = int(getattr(salida, "status", salida))     # PuLP 3+/4
    return pulp.LpSolveStatus(codigo).name


def valor(x):
    v = pulp.value(x)
    return 0.0 if v is None else float(v)


def nombre_solver():
    return type(_solver()).__name__
