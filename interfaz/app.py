"""
GUARDIA — interfaz web (Streamlit).

    streamlit run interfaz/app.py
"""

import sys
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ))

import altair as alt
import pandas as pd
import streamlit as st

from turnos import Parametros, resolver, cuadrante, validar, resumen
from turnos.datos import COSTO_ACTUAL, TIPOS
from ia.prediccion_demanda import cobertura_predicha

st.set_page_config(page_title="GUARDIA · Turnos inteligentes de urgencias", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="expanded")

# ------------------------------------------------------------------ estilos
DARK, TEAL, TEAL_S, ORANGE, LIGHT, INK, BODY = "#0E2A3B", "#17707E", "#7FC8D1", "#C85A1E", "#F5F7F6", "#15303E", "#4A5A64"
COLOR_TURNO = {"Mañana": ("#FFF1D6", "#8A5A00"), "Tarde": ("#D9EFF1", "#0F5864"),
               "Noche": ("#1D3B4F", "#E6F2F4"), "Descanso": ("#EEF1F1", "#8A979E")}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@500;600;700&family=Public+Sans:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stMarkdown, p, label, li {{ font-family: 'Public Sans', sans-serif; }}
h1, h2, h3, h4 {{ font-family: 'Rubik', sans-serif !important; color: {INK}; }}
.stApp {{ background: {LIGHT}; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px; }}
header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer {{ visibility: hidden; }}

section[data-testid="stSidebar"] {{ background: {DARK}; }}
section[data-testid="stSidebar"] * {{ color: #DCE8EB !important; }}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{ color: #FFFFFF !important; }}
section[data-testid="stSidebar"] input {{ color: {INK} !important; }}
section[data-testid="stSidebar"] [data-baseweb="select"] * {{ color: {INK} !important; }}
section[data-testid="stSidebar"] .stExpander {{ border: 1px solid rgba(255,255,255,.12); border-radius: 12px; background: rgba(255,255,255,.03); }}
.side-brand {{ font-family: 'Rubik', sans-serif; font-size: 30px; font-weight: 700; color: #fff !important; letter-spacing: 1px; }}
.side-sub {{ font-size: 12.5px; color: {TEAL_S} !important; margin-top: -4px; margin-bottom: 14px; }}

.hero {{ background: linear-gradient(120deg, {DARK} 0%, #12465A 55%, {TEAL} 100%); border-radius: 22px;
        padding: 34px 40px; color: #fff; position: relative; overflow: hidden; margin-bottom: 22px;
        box-shadow: 0 18px 40px rgba(14,42,59,.22); }}
.hero:after {{ content: ""; position: absolute; right: -80px; top: -80px; width: 320px; height: 320px;
              border-radius: 50%; background: rgba(127,200,209,.14); }}
.hero .eyebrow {{ font-size: 13px; letter-spacing: 3px; text-transform: uppercase; color: {TEAL_S}; font-weight: 700; }}
.hero h1 {{ font-size: 64px; line-height: 1; margin: 8px 0 6px; color: #fff !important; letter-spacing: 2px; }}
.hero .acr {{ font-family: 'Rubik', sans-serif; font-size: 19px; color: #CFE9EC; }}
.hero .acr b {{ color: #fff; }}
.hero .tag {{ font-size: 16px; color: #BFD6DB; margin-top: 12px; max-width: 760px; }}
.badges {{ margin-top: 18px; display: flex; gap: 8px; flex-wrap: wrap; position: relative; z-index: 1; }}
.badge {{ background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.22); color: #fff;
          padding: 6px 14px; border-radius: 999px; font-size: 13px; font-weight: 600; }}

.kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 18px; }}
.kpi {{ background: #fff; border-radius: 18px; padding: 20px 22px; box-shadow: 0 4px 18px rgba(14,42,59,.07);
        border-top: 5px solid {TEAL}; }}
.kpi.or {{ border-top-color: {ORANGE}; }}
.kpi .lab {{ font-size: 13px; color: {BODY}; font-weight: 600; letter-spacing: .5px; text-transform: uppercase; }}
.kpi .val {{ font-family: 'Rubik', sans-serif; font-size: 40px; font-weight: 700; color: {INK}; margin-top: 6px; line-height: 1.1; }}
.kpi .sub {{ font-size: 14px; color: {BODY}; margin-top: 4px; }}
.pill-ok {{ display: inline-block; background: #E2F4EA; color: #1C6B3F; padding: 2px 10px; border-radius: 999px; font-weight: 700; font-size: 13px; }}
.pill-bad {{ display: inline-block; background: #FBE3DA; color: #9A3A12; padding: 2px 10px; border-radius: 999px; font-weight: 700; font-size: 13px; }}

.card {{ background: #fff; border-radius: 18px; padding: 22px 24px; box-shadow: 0 4px 18px rgba(14,42,59,.07); margin-bottom: 16px; }}
.card h3 {{ margin: 0 0 4px; font-size: 22px; }}
.card .muted {{ color: {BODY}; font-size: 14px; margin-bottom: 14px; }}

table.grid {{ width: 100%; border-collapse: separate; border-spacing: 6px; }}
table.grid th {{ font-family: 'Rubik', sans-serif; font-size: 14px; color: {BODY}; font-weight: 600; text-align: center; padding: 4px; }}
table.grid td {{ text-align: center; }}
table.grid td.prof {{ font-family: 'Rubik', sans-serif; font-weight: 700; color: {INK}; text-align: left; font-size: 15px; white-space: nowrap; }}
table.grid td.num {{ font-weight: 700; color: {INK}; font-size: 15px; }}
.chip {{ display: block; border-radius: 10px; padding: 9px 6px; font-weight: 600; font-size: 13.5px; }}
.chip small {{ display: block; font-weight: 500; opacity: .8; font-size: 11.5px; }}
.legend {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 10px; font-size: 13px; color: {BODY}; }}
.legend span i {{ display: inline-block; width: 14px; height: 14px; border-radius: 4px; margin-right: 6px; vertical-align: -2px; }}

.check {{ display: flex; gap: 10px; align-items: center; padding: 10px 0; border-bottom: 1px solid #EEF2F2; font-size: 15px; }}
.check .ic {{ width: 26px; height: 26px; border-radius: 50%; background: #E2F4EA; color: #1C6B3F; display: flex;
              align-items: center; justify-content: center; font-weight: 800; }}
.check .ic.bad {{ background: #FBE3DA; color: #9A3A12; }}

.stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: #fff; padding: 6px; border-radius: 14px; box-shadow: 0 4px 18px rgba(14,42,59,.06); }}
.stTabs [data-baseweb="tab"] {{ border-radius: 10px; padding: 10px 18px; font-weight: 600; }}
.stTabs [aria-selected="true"] {{ background: {DARK}; color: #fff !important; }}
.stTabs [aria-selected="true"] p {{ color: #fff !important; }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none; }}
.stDownloadButton button, .stButton button {{ background: {TEAL}; color: #fff; border: 0; border-radius: 10px; font-weight: 700; padding: .55rem 1.1rem; }}
.stDownloadButton button:hover, .stButton button:hover {{ background: {DARK}; color: #fff; }}

.ct {{ margin: 0 0 4px !important; font-size: 22px !important; }}
div[data-testid="stVerticalBlockBorderWrapper"] {{ background: #fff; border-radius: 18px !important; border: 0 !important;
     box-shadow: 0 4px 18px rgba(14,42,59,.07); padding: 8px 10px; }}
.stMarkdown table.grid, .stMarkdown table.grid tr, .stMarkdown table.grid td, .stMarkdown table.grid th {{ border: none !important; background: transparent !important; }}
section[data-testid="stSidebar"] details summary {{ background: transparent !important; }}
section[data-testid="stSidebar"] details summary:hover {{ background: rgba(255,255,255,.06) !important; }}
section[data-testid="stSidebar"] details {{ background: transparent !important; }}
section[data-testid="stSidebar"] [data-testid="stNumberInput"] button {{ color: {INK} !important; }}
section[data-testid="stSidebar"] [data-testid="stNumberInput"] button * {{ color: {INK} !important; fill: {INK} !important; }}
[data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}
.foot {{ text-align: center; color: #7A8A93; font-size: 13px; margin-top: 26px; padding-top: 16px; border-top: 1px solid #E1E7E7; }}
@media (max-width: 900px) {{ .kpis {{ grid-template-columns: repeat(2, 1fr); }} .hero h1 {{ font-size: 46px; }} }}
</style>
""", unsafe_allow_html=True)


def html(s: str):
    st.markdown(s, unsafe_allow_html=True)


def usd(v) -> str:
    return "$" + f"{v:,.0f}".replace(",", ".")


# ------------------------------------------------------------------ panel lateral
with st.sidebar:
    html('<div class="side-brand">🛡️ GUARDIA</div>'
         '<div class="side-sub">Panel de control del escenario</div>')
    with st.expander("👩‍⚕️ Personal", expanded=True):
        n_prof = st.slider("Profesionales disponibles", 4, 12, 8)
        max_turnos = st.slider("Máximo de turnos por persona", 1, 5, 4, help="El límite legal del enunciado es 4.")
    with st.expander("💲 Costo por turno (USD)", expanded=False):
        c1 = st.number_input("Mañana", 0, 1000, 120, 10)
        c2 = st.number_input("Tarde", 0, 1000, 140, 10)
        c3 = st.number_input("Noche", 0, 1000, 200, 10)
    with st.expander("📋 Cobertura mínima", expanded=True):
        modo = st.radio("Origen", ["Enunciado (3-3-2)", "Predicción con IA"], horizontal=False)
        if modo == "Enunciado (3-3-2)":
            r1 = st.number_input("Mañana ", 0, 10, 3)
            r2 = st.number_input("Tarde ", 0, 10, 3)
            r3 = st.number_input("Noche ", 0, 10, 2)
        else:
            r1, r2, r3 = 3, 3, 2
            dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            inicio = dias.index(st.selectbox("El ciclo empieza el", dias))
            festivos = st.multiselect("Días festivos del ciclo", [1, 2, 3, 4, 5])
            lluvias = int(st.toggle("Temporada de lluvias", True))
    with st.expander("🧑‍🔧 Personal externo", expanded=False):
        usar_ext = st.toggle("Permitir externos planificados", True)
        prima = st.slider("Recargo del externo (%)", 0, 150, 50, 5) / 100
        equidad = st.toggle("Repartir 1 o 2 noches por persona", True)

p = Parametros(n_profesionales=n_prof, max_turnos=max_turnos,
               costo_tipo={1: c1, 2: c2, 3: c3}, cobertura_tipo={1: r1, 2: r2, 3: r3},
               usar_externos=usar_ext, prima_externo=prima, equidad_noches=equidad)

detalle_ia, met = None, None
if modo == "Predicción con IA":
    R, detalle_ia, met = cobertura_predicha(inicio, tuple(festivos), lluvias)
    p = replace(p, cobertura_por_turno=R)

# ------------------------------------------------------------------ encabezado
html(f"""
<div class="hero">
  <div class="eyebrow">Universidad de La Guajira · Ingeniería de Sistemas</div>
  <h1>GUARDIA</h1>
  <div class="acr"><b>G</b>estión <b>U</b>nificada de <b>A</b>signación de <b>R</b>ecursos y <b>D</b>emanda con <b>I</b>nteligencia <b>A</b>rtificial</div>
  <div class="tag">Programa los turnos de urgencias al menor costo posible, cumpliendo siempre la normativa laboral y ajustándose a la demanda real de pacientes.</div>
  <div class="badges"><span class="badge">Programación Entera Binaria</span><span class="badge">PuLP · CBC</span>
  <span class="badge">Predicción de demanda con IA</span><span class="badge">{'Cobertura por IA' if detalle_ia is not None else 'Cobertura 3-3-2'}</span></div>
</div>""")

# ------------------------------------------------------------------ optimización
with st.spinner("Calculando el cuadrante óptimo..."):
    res = resolver(p)

if not res.optimo:
    demanda = sum(p.R(t) for t in p.turnos)
    html(f"""<div class="card" style="border-left:6px solid {ORANGE};">
    <h3>⚠️ El escenario no tiene solución</h3>
    <div class="muted">Se necesitan <b>{demanda}</b> asignaciones y el personal interno solo cubre
    <b>{n_prof} × {max_turnos} = {n_prof * max_turnos}</b>. Active el personal externo o aumente la capacidad.</div></div>""")
    st.stop()

errores = validar(res)
r = resumen(res)
ahorro_pct = r["Ahorro (%)"]
html(f"""
<div class="kpis">
  <div class="kpi"><div class="lab">Costo total del ciclo</div><div class="val">{usd(r['Costo total (USD)'])}</div>
    <div class="sub">Interno {usd(r['Costo interno (USD)'])} · Externo {usd(r['Costo externo (USD)'])}</div></div>
  <div class="kpi or"><div class="lab">Ahorro frente a hoy</div><div class="val">{usd(r['Ahorro vs. actual (USD)'])}</div>
    <div class="sub"><span class="{'pill-ok' if ahorro_pct >= 0 else 'pill-bad'}">{'▼' if ahorro_pct >= 0 else '▲'} {abs(ahorro_pct)} %</span> vs. {usd(COSTO_ACTUAL)}</div></div>
  <div class="kpi"><div class="lab">Turnos con externos</div><div class="val">{r['Turnos externos']}</div>
    <div class="sub">planificados, no de urgencia</div></div>
  <div class="kpi"><div class="lab">Normativa laboral</div><div class="val">{'100 %' if not errores else f'{len(errores)} fallas'}</div>
    <div class="sub"><span class="{'pill-ok' if not errores else 'pill-bad'}">{'✓ Todas las reglas se cumplen' if not errores else 'Revisar'}</span></div></div>
</div>""")

tab1, tab2, tab3, tab4 = st.tabs(["🗓️  Cuadrante", "📊  Costos", "🤖  Predicción IA", "🧮  Modelo y validación"])

# ------------------------------------------------------------------ cuadrante
with tab1:
    filas = ""
    for k in p.profesionales:
        celdas = ""
        for d in p.dias:
            t = next((t for t in p.turnos if p.dia_de(t) == d and res.asignacion[k, t]), None)
            tipo = TIPOS[p.tipo_de(t)] if t else "Descanso"
            bg, fg = COLOR_TURNO[tipo]
            sub = f"<small>t{t}</small>" if t else "<small>&nbsp;</small>"
            celdas += f'<td><span class="chip" style="background:{bg};color:{fg};">{tipo}{sub}</span></td>'
        turnos_k = sum(res.asignacion[k, t] for t in p.turnos)
        costo_k = sum(p.C(t) for t in p.turnos if res.asignacion[k, t])
        filas += f'<tr><td class="prof">{k.upper()}</td>{celdas}<td class="num">{turnos_k}</td><td class="num">{usd(costo_k)}</td></tr>'
    if p.usar_externos:
        celdas = ""
        for d in p.dias:
            n = sum(res.externos[t] for t in p.turnos if p.dia_de(t) == d)
            txt = f"{n} externo{'s' if n != 1 else ''}" if n else "—"
            celdas += f'<td><span class="chip" style="background:#FBE7DB;color:#8A3A10;">{txt}<small>&nbsp;</small></span></td>'
        filas += (f'<tr><td class="prof" style="color:{ORANGE};">EXTERNOS</td>{celdas}'
                  f'<td class="num">{res.turnos_externos}</td><td class="num">{usd(res.costo_externo)}</td></tr>')
    cab = "".join(f"<th>Día {d}</th>" for d in p.dias)
    leyenda = "".join(f'<span><i style="background:{bg};border:1px solid #d5dede;"></i>{n}</span>'
                      for n, (bg, _) in COLOR_TURNO.items())
    html(f"""<div class="card"><h3>Cuadrante óptimo de turnos</h3>
    <div class="muted">Generado automáticamente por el modelo en menos de un segundo.</div>
    <table class="grid"><tr><th style="text-align:left;">Profesional</th>{cab}<th>Turnos</th><th>Costo</th></tr>{filas}</table>
    <div class="legend">{leyenda}<span><i style="background:#FBE7DB;border:1px solid #d5dede;"></i>Externos</span></div></div>""")
    cua = cuadrante(res)
    st.download_button("⬇️  Descargar cuadrante (CSV)", cua.to_csv(index=False).encode("utf-8-sig"),
                       "cuadrante_guardia.csv", "text/csv")

# ------------------------------------------------------------------ costos
with tab2:
    a, b = st.columns([1.15, 1])
    with a:
        caja = st.container(border=True)
        caja.markdown('<h3 class="ct">Costo por ciclo</h3><div class="muted">Programación actual frente a GUARDIA.</div>', unsafe_allow_html=True)
        df = pd.DataFrame([
            {"Escenario": "Actual (manual)", "Componente": "Costo actual", "USD": COSTO_ACTUAL},
            {"Escenario": "GUARDIA", "Componente": "Personal interno", "USD": res.costo_interno},
            {"Escenario": "GUARDIA", "Componente": "Externos planificados", "USD": res.costo_externo},
        ])
        ch = alt.Chart(df).mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8, size=90).encode(
            x=alt.X("Escenario:N", sort=["Actual (manual)", "GUARDIA"], title=None, axis=alt.Axis(labelAngle=0, labelFontSize=14)),
            y=alt.Y("sum(USD):Q", title="USD por ciclo"),
            color=alt.Color("Componente:N", scale=alt.Scale(domain=["Costo actual", "Personal interno", "Externos planificados"],
                            range=["#9AA6AD", TEAL, TEAL_S]), legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["Escenario", "Componente", alt.Tooltip("USD:Q", format=",.0f")],
        ).properties(height=340)
        caja.altair_chart(ch, width="stretch")
    with b:
        caja2 = st.container(border=True)
        caja2.markdown('<h3 class="ct">Costo por profesional</h3><div class="muted">Reparto de la carga en el ciclo.</div>', unsafe_allow_html=True)
        dk = pd.DataFrame({"Profesional": [k.upper() for k in p.profesionales],
                           "USD": [sum(p.C(t) for t in p.turnos if res.asignacion[k, t]) for k in p.profesionales]})
        ch2 = alt.Chart(dk).mark_bar(cornerRadiusEnd=6, color=TEAL).encode(
            y=alt.Y("Profesional:N", sort=None, title=None), x=alt.X("USD:Q", title="USD"),
            tooltip=["Profesional", alt.Tooltip("USD:Q", format=",.0f")]).properties(height=340)
        caja2.altair_chart(ch2, width="stretch")
    sobre_actual = COSTO_ACTUAL - 5900
    sobre_opt = max(res.total - sum(p.C(t) * p.R(t) for t in p.turnos), 0)
    html(f"""<div class="card"><h3>Sobrecosto por reemplazos</h3>
    <div class="muted">Diferencia frente al costo salarial mínimo para cubrir la demanda.</div>
    <div class="kpis" style="grid-template-columns:repeat(3,1fr);margin:0;">
      <div class="kpi" style="box-shadow:none;background:{LIGHT};"><div class="lab">Hoy</div><div class="val">{usd(sobre_actual)}</div></div>
      <div class="kpi" style="box-shadow:none;background:{LIGHT};"><div class="lab">Con GUARDIA</div><div class="val">{usd(sobre_opt)}</div></div>
      <div class="kpi or" style="box-shadow:none;background:{LIGHT};"><div class="lab">Reducción</div>
        <div class="val">{(1 - sobre_opt / sobre_actual) * 100:.1f} %</div></div>
    </div></div>""")

# ------------------------------------------------------------------ IA
with tab3:
    if detalle_ia is None:
        html(f"""<div class="card" style="text-align:center;padding:40px;">
        <div style="font-size:46px;">🤖</div><h3>Active la predicción de demanda</h3>
        <div class="muted" style="max-width:560px;margin:8px auto 0;">En el panel lateral, en <b>Cobertura mínima</b>, elija
        <b>Predicción con IA</b>. El modelo estimará los pacientes de cada turno y ajustará la cobertura antes de optimizar.</div></div>""")
    else:
        html(f"""<div class="kpis" style="grid-template-columns:repeat(3,1fr);">
        <div class="kpi"><div class="lab">Error medio del modelo</div><div class="val">{met['MAE']:.1f}</div><div class="sub">pacientes por turno</div></div>
        <div class="kpi"><div class="lab">R² en prueba</div><div class="val">{met['R2']:.2f}</div><div class="sub">regresión lineal múltiple</div></div>
        <div class="kpi or"><div class="lab">Cobertura requerida</div><div class="val">{sum(p.R(t) for t in p.turnos)}</div><div class="sub">asignaciones (base: 40)</div></div>
        </div>""")
        d = detalle_ia.copy()
        d["Turno"] = d["turno"].map(TIPOS)
        d["Día"] = "Día " + d["dia"].astype(str)
        caja3 = st.container(border=True)
        caja3.markdown('<h3 class="ct">Pacientes esperados por turno</h3><div class="muted">Predicción del módulo de IA para el ciclo seleccionado.</div>', unsafe_allow_html=True)
        ch3 = alt.Chart(d).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Día:N", title=None, axis=alt.Axis(labelAngle=0)), xOffset="Turno:N",
            y=alt.Y("pacientes_estimados:Q", title="Pacientes"),
            color=alt.Color("Turno:N", scale=alt.Scale(domain=["Mañana", "Tarde", "Noche"], range=["#E8B04A", TEAL, DARK]),
                            legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["Día", "Turno", "pacientes_estimados", "R_t"]).properties(height=320)
        caja3.altair_chart(ch3, width="stretch")
        piv = d.pivot(index="Turno", columns="Día", values="R_t").reindex(["Mañana", "Tarde", "Noche"])
        caja4 = st.container(border=True)
        caja4.markdown('<h3 class="ct">Profesionales requeridos (R<sub>t</sub>)</h3><div class="muted">Lo que recibe el modelo de optimización.</div>', unsafe_allow_html=True)
        caja4.dataframe(piv, width="stretch")

# ------------------------------------------------------------------ modelo
with tab4:
    a, b = st.columns([1.2, 1])
    with a:
        caja5 = st.container(border=True)
        caja5.markdown('<h3 class="ct">Formulación matemática</h3><div class="muted">Programación Entera Binaria resuelta con PuLP y CBC.</div>', unsafe_allow_html=True)
        caja5.latex(r"\min Z=\sum_{k} y_k+\sum_{t}(1+\alpha)\,C_t\,z_t")
        caja5.latex(r"y_k=\sum_t C_t\,x_{kt}\qquad x_{kt}\in\{0,1\},\; z_t\in\mathbb{Z}^+")
        caja5.latex(r"\sum_k x_{kt}+z_t\ge R_t \qquad \sum_{t\in T_d}x_{kt}\le 1")
        caja5.latex(r"x_{kt}+x_{k,t+1}\le 1\;(t\ \text{noche}) \qquad \sum_t x_{kt}\le %d" % p.max_turnos)
    with b:
        reglas = [
            ("Cobertura mínima en los 15 turnos", not any("Cobertura" in e for e in errores)),
            ("Máximo un turno por día", not any("más de un turno" in e for e in errores)),
            ("Descanso después de cada noche", not any("después de la noche" in e for e in errores)),
            (f"Máximo {p.max_turnos} turnos por profesional", not any("supera" in e for e in errores)),
        ]
        filas = "".join(f'<div class="check"><div class="ic{"" if ok else " bad"}">{"✓" if ok else "✕"}</div>{txt}</div>'
                        for txt, ok in reglas)
        html(f'<div class="card"><h3>Validación independiente</h3><div class="muted">Cada regla se comprueba sin usar el solver.</div>{filas}</div>')

html("""<div class="foot"><b>GUARDIA</b> · Investigación de Operaciones + Desarrollo Tecnológico + IA ·
Universidad de La Guajira · Ingeniería de Sistemas · Docente: Nicolas Sánchez Vázquez</div>""")
