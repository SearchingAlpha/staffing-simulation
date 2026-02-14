import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config & constants
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Calculadora de Costes de Personal 3PL · HireRobots",
    page_icon="📦",
    layout="wide",
)

RED = "#E74C3C"
RED_LIGHT = "rgba(231,76,60,0.12)"
GREEN = "#27AE60"
GREEN_LIGHT = "rgba(39,174,96,0.12)"
GREY = "#95A5A6"

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Banner principal de ahorro */
    .savings-banner {
        background: linear-gradient(135deg, #27AE60 0%, #2ECC71 100%);
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        margin: 1rem 0 2rem 0;
    }
    .savings-banner h1 {
        color: white !important;
        font-size: 3rem !important;
        margin: 0 !important;
    }
    .savings-banner p {
        color: rgba(255,255,255,0.9);
        font-size: 1.15rem;
        margin: 0.5rem 0 0 0;
    }

    /* Tarjetas de escenario */
    .scenario-card {
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .scenario-bad  { background: rgba(231,76,60,0.07); border-left: 5px solid #E74C3C; }
    .scenario-good { background: rgba(39,174,96,0.07); border-left: 5px solid #27AE60; }
    .scenario-card h3 { margin-top: 0; }
    .scenario-card .big-num { font-size: 2rem; font-weight: 700; }
    .scenario-card .detail { color: #555; font-size: 0.95rem; margin: 0.3rem 0; }

    /* Cajas explicativas */
    .explainer {
        background: #F8F9FA;
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        font-size: 0.95rem;
        color: #333;
        line-height: 1.55;
    }

    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stSlider label {
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Encabezado
# ---------------------------------------------------------------------------
st.title("📦 ¿Cuánto te cuesta una mala planificación de personal?")
st.markdown(
    "Ajusta los números en la barra lateral para que coincidan con tu operación. "
    "Descubre exactamente cuánto dinero pierdes sin un pronóstico de demanda — "
    "y cuánto ahorras con uno."
)

# ---------------------------------------------------------------------------
# Barra lateral — inputs
# ---------------------------------------------------------------------------
st.sidebar.header("Tu Almacén")
units_per_week = st.sidebar.number_input(
    "Unidades movidas por semana",
    min_value=1_000, max_value=500_000, value=30_000, step=1_000,
    help="Total de unidades (picks, packs, envíos) que tu almacén maneja semanalmente.",
)
units_per_worker_per_week = st.sidebar.number_input(
    "Unidades que maneja un operario por semana",
    min_value=100, max_value=5_000, value=600, step=50,
    help="Productividad media de un operario de almacén a tiempo completo.",
)

st.sidebar.header("Costes Laborales")
hourly_rate = st.sidebar.number_input(
    "Salario por hora (€)", min_value=5.0, max_value=50.0, value=12.50, step=0.50,
)
hours_per_week = st.sidebar.number_input(
    "Horas por semana", min_value=20, max_value=60, value=40, step=1,
)
overtime_multiplier = st.sidebar.number_input(
    "Multiplicador de horas extra",
    min_value=1.0, max_value=3.0, value=1.25, step=0.05,
    help="Ej: 1.25 significa que las horas extra cuestan un 25% más que las normales.",
)

st.sidebar.header("Precisión del Staffing")
misallocation_no_forecast = st.sidebar.slider(
    "Error de personal SIN pronóstico (%)",
    10, 50, 20, 1,
    help="Cuánto se desvía tu plantilla de la necesidad real en una semana típica, sin pronóstico de demanda.",
)
misallocation_with_forecast = st.sidebar.slider(
    "Error de personal CON pronóstico (%)",
    0, 20, 5, 1,
    help="Cuánto se desvía tu plantilla cuando usas un buen pronóstico de demanda.",
)

st.sidebar.header("Penalizaciones")
sla_penalty_per_miss = st.sidebar.number_input(
    "Penalización SLA por semana incumplida (€)",
    min_value=0, max_value=50_000, value=500, step=100,
    help="Coste medio de penalización cuando no cumples objetivos por falta de personal.",
)

# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------
required_workers = units_per_week / units_per_worker_per_week
weekly_worker_cost = hourly_rate * hours_per_week


def scenario_costs(misalloc_pct: float) -> dict:
    frac = misalloc_pct / 100.0
    over = required_workers * frac / 2
    under = required_workers * frac / 2

    weekly_overstaffing = over * weekly_worker_cost
    weekly_overtime_premium = under * weekly_worker_cost * (overtime_multiplier - 1)
    weekly_sla = sla_penalty_per_miss / 2

    annual_overstaffing = weekly_overstaffing * 52
    annual_overtime = weekly_overtime_premium * 52
    annual_sla = weekly_sla * 52

    return {
        "workers_over": over,
        "workers_under": under,
        "monthly_overstaffing": annual_overstaffing / 12,
        "monthly_overtime": annual_overtime / 12,
        "monthly_sla": annual_sla / 12,
        "annual_overstaffing": annual_overstaffing,
        "annual_overtime": annual_overtime,
        "annual_sla": annual_sla,
        "annual_total": annual_overstaffing + annual_overtime + annual_sla,
    }


no_fc = scenario_costs(misallocation_no_forecast)
with_fc = scenario_costs(misallocation_with_forecast)
annual_savings = no_fc["annual_total"] - with_fc["annual_total"]

# ---------------------------------------------------------------------------
# 1 ▸ BANNER DE AHORRO
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="savings-banner">
        <p>Con un pronóstico de demanda ahorras</p>
        <h1>€{annual_savings:,.0f} / año</h1>
        <p>Son <b>€{annual_savings / 12:,.0f}</b> cada mes que vuelven a tu margen.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 2 ▸ CONTEXTO EN LENGUAJE SENCILLO
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="explainer">
        Tu almacén mueve <b>{units_per_week:,} unidades/semana</b>.
        Eso requiere aproximadamente <b>{required_workers:.0f} operarios</b>.
        Sin un pronóstico, el personal se desvía ~<b>{misallocation_no_forecast}%</b> —
        eso son <b>{no_fc['workers_over']:.0f} operarios de más</b> en semanas flojas
        y <b>{no_fc['workers_under']:.0f} operarios de menos</b> en semanas pico.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 3 ▸ TARJETAS LADO A LADO
# ---------------------------------------------------------------------------
st.markdown("### ¿A dónde se va el dinero?")

col_bad, col_good = st.columns(2)

with col_bad:
    st.markdown(
        f"""
        <div class="scenario-card scenario-bad">
            <h3>❌ Sin Pronóstico</h3>
            <p class="detail">Error de personal: <b>{misallocation_no_forecast}%</b></p>
            <p class="detail">
                🧑‍🤝‍🧑 <b>{no_fc['workers_over']:.0f}</b> operarios de más en semanas flojas
                → <span class="big-num" style="color:{RED};">€{no_fc['monthly_overstaffing']:,.0f}</span>/mes desperdiciados
            </p>
            <p class="detail">
                🔥 <b>{no_fc['workers_under']:.0f}</b> operarios de menos en semanas pico → horas extra a {overtime_multiplier}×
                → <span class="big-num" style="color:{RED};">€{no_fc['monthly_overtime']:,.0f}</span>/mes extra
            </p>
            <p class="detail">
                ⚠️ Penalizaciones SLA
                → <span class="big-num" style="color:{RED};">€{no_fc['monthly_sla']:,.0f}</span>/mes
            </p>
            <hr>
            <p class="detail" style="font-size:1.1rem;">
                Desperdicio anual total: <span class="big-num" style="color:{RED};">€{no_fc['annual_total']:,.0f}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_good:
    accuracy = 100 - misallocation_with_forecast
    st.markdown(
        f"""
        <div class="scenario-card scenario-good">
            <h3>✅ Con Pronóstico ({accuracy}% de precisión)</h3>
            <p class="detail">Error de personal: <b>{misallocation_with_forecast}%</b></p>
            <p class="detail">
                🧑‍🤝‍🧑 <b>{with_fc['workers_over']:.0f}</b> operarios de más en semanas flojas
                → <span class="big-num" style="color:{GREEN};">€{with_fc['monthly_overstaffing']:,.0f}</span>/mes
            </p>
            <p class="detail">
                🔥 <b>{with_fc['workers_under']:.0f}</b> operarios de menos en semanas pico
                → <span class="big-num" style="color:{GREEN};">€{with_fc['monthly_overtime']:,.0f}</span>/mes
            </p>
            <p class="detail">
                ⚠️ Penalizaciones SLA
                → <span class="big-num" style="color:{GREEN};">€{with_fc['monthly_sla']:,.0f}</span>/mes
            </p>
            <hr>
            <p class="detail" style="font-size:1.1rem;">
                Desperdicio anual total: <span class="big-num" style="color:{GREEN};">€{with_fc['annual_total']:,.0f}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# 4 ▸ GRÁFICO — Desglose de costes
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### Desglose Anual de Costes: Antes vs Después del Pronóstico")
st.markdown(
    '<div class="explainer">'
    "Cada barra muestra de dónde viene el desperdicio laboral. "
    "La <b style='color:#E74C3C'>barra roja</b> es tu coste hoy sin pronóstico. "
    "La <b style='color:#27AE60'>barra verde</b> es tu coste con un pronóstico de demanda. "
    "La diferencia entre ambas es dinero que te quedas."
    "</div>",
    unsafe_allow_html=True,
)

categories = [
    "Operarios ociosos<br>(sobredotación)",
    "Primas de<br>horas extra",
    "Penalizaciones<br>SLA",
]
no_fc_vals = [no_fc["annual_overstaffing"], no_fc["annual_overtime"], no_fc["annual_sla"]]
with_fc_vals = [with_fc["annual_overstaffing"], with_fc["annual_overtime"], with_fc["annual_sla"]]

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name="Sin Pronóstico",
    x=categories, y=no_fc_vals,
    marker_color=RED,
    text=[f"€{v:,.0f}" for v in no_fc_vals],
    textposition="outside",
    textfont=dict(size=14, color=RED),
))
fig_bar.add_trace(go.Bar(
    name="Con Pronóstico",
    x=categories, y=with_fc_vals,
    marker_color=GREEN,
    text=[f"€{v:,.0f}" for v in with_fc_vals],
    textposition="outside",
    textfont=dict(size=14, color=GREEN),
))
fig_bar.update_layout(
    barmode="group",
    yaxis_title="Coste Anual (€)",
    template="plotly_white",
    height=420,
    font=dict(size=14),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=14)),
    margin=dict(t=60),
)
st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------------------------
# 5 ▸ GRÁFICO — Simulación semanal (52 semanas)
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### Cómo se ve un año típico — Semana a semana")
st.markdown(
    '<div class="explainer">'
    "Esta simulación muestra 52 semanas de planificación de personal. "
    "La <b>línea negra discontinua</b> es cuántos operarios realmente necesitabas. "
    "La <b style='color:#E74C3C'>línea roja</b> es lo que programarías sin pronóstico (adivinando). "
    "La <b style='color:#27AE60'>línea verde</b> es lo que programarías con un pronóstico. "
    "Cada hueco entre las líneas es dinero perdido."
    "</div>",
    unsafe_allow_html=True,
)

np.random.seed(42)
demand = np.random.normal(loc=units_per_week, scale=units_per_week * 0.15, size=52)
demand = np.clip(demand, units_per_week * 0.5, units_per_week * 1.5)
actual_needed = demand / units_per_worker_per_week

# Sin pronóstico: se programa la media cada semana (no se ven los picos)
no_fc_staff = np.full(52, required_workers) + np.random.normal(
    0, required_workers * misallocation_no_forecast / 200, 52
)
no_fc_staff = np.clip(no_fc_staff, 1, None)

# Con pronóstico: se sigue la demanda real de cerca
with_fc_staff = actual_needed + np.random.normal(
    0, required_workers * misallocation_with_forecast / 200, 52
)
with_fc_staff = np.clip(with_fc_staff, 1, None)

weeks = np.arange(1, 53)

fig_sim = go.Figure()

# Zona sombreada — error sin pronóstico
fig_sim.add_trace(go.Scatter(
    x=np.concatenate([weeks, weeks[::-1]]),
    y=np.concatenate([np.maximum(actual_needed, no_fc_staff),
                      np.minimum(actual_needed, no_fc_staff)[::-1]]),
    fill="toself",
    fillcolor=RED_LIGHT,
    line=dict(width=0),
    name="Desperdicio (sin pronóstico)",
    hoverinfo="skip",
))

# Zona sombreada — error con pronóstico
fig_sim.add_trace(go.Scatter(
    x=np.concatenate([weeks, weeks[::-1]]),
    y=np.concatenate([np.maximum(actual_needed, with_fc_staff),
                      np.minimum(actual_needed, with_fc_staff)[::-1]]),
    fill="toself",
    fillcolor=GREEN_LIGHT,
    line=dict(width=0),
    name="Desperdicio (con pronóstico)",
    hoverinfo="skip",
))

# Líneas
fig_sim.add_trace(go.Scatter(
    x=weeks, y=actual_needed, mode="lines",
    name="Operarios realmente necesarios",
    line=dict(color="black", width=2, dash="dash"),
))
fig_sim.add_trace(go.Scatter(
    x=weeks, y=no_fc_staff, mode="lines",
    name="Programados — sin pronóstico",
    line=dict(color=RED, width=2),
))
fig_sim.add_trace(go.Scatter(
    x=weeks, y=with_fc_staff, mode="lines",
    name="Programados — con pronóstico",
    line=dict(color=GREEN, width=2),
))

fig_sim.update_layout(
    xaxis_title="Semana del año",
    yaxis_title="Número de operarios",
    template="plotly_white",
    height=450,
    font=dict(size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=13)),
    margin=dict(t=60),
)
st.plotly_chart(fig_sim, use_container_width=True)

# ---------------------------------------------------------------------------
# 6 ▸ GRÁFICO — Sensibilidad: ¿cuánto importa la precisión?
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown("### ¿Cuánto importa la precisión del pronóstico?")
st.markdown(
    '<div class="explainer">'
    "Este gráfico muestra cómo cambia tu desperdicio anual a medida que mejora la precisión del personal. "
    "Cuanto más a la derecha estés, peores son tus estimaciones — y más dinero pierdes. "
    "Los dos puntos muestran dónde estás <b>hoy</b> (sin pronóstico) y dónde <b>podrías estar</b>."
    "</div>",
    unsafe_allow_html=True,
)

misalloc_range = np.arange(0, 51, 1)
annual_totals = [scenario_costs(m)["annual_total"] for m in misalloc_range]

fig_sens = go.Figure()

# Relleno del área
fig_sens.add_trace(go.Scatter(
    x=misalloc_range, y=annual_totals,
    mode="lines",
    line=dict(color=GREY, width=2),
    fill="tozeroy",
    fillcolor="rgba(149,165,166,0.10)",
    showlegend=False,
))

# Puntos con etiquetas
fig_sens.add_trace(go.Scatter(
    x=[misallocation_no_forecast],
    y=[no_fc["annual_total"]],
    mode="markers+text",
    marker=dict(size=18, color=RED, symbol="circle"),
    text=[f"  Hoy: €{no_fc['annual_total']:,.0f}"],
    textposition="middle right",
    textfont=dict(size=14, color=RED),
    name="Sin pronóstico",
))
fig_sens.add_trace(go.Scatter(
    x=[misallocation_with_forecast],
    y=[with_fc["annual_total"]],
    mode="markers+text",
    marker=dict(size=18, color=GREEN, symbol="circle"),
    text=[f"  Con pronóstico: €{with_fc['annual_total']:,.0f}"],
    textposition="middle right",
    textfont=dict(size=14, color=GREEN),
    name="Con pronóstico",
))

# Flecha entre los dos puntos
fig_sens.add_annotation(
    x=misallocation_no_forecast,
    y=no_fc["annual_total"],
    ax=misallocation_with_forecast,
    ay=with_fc["annual_total"],
    xref="x", yref="y", axref="x", ayref="y",
    showarrow=True,
    arrowhead=3, arrowsize=1.5, arrowwidth=2,
    arrowcolor=GREEN,
)
fig_sens.add_annotation(
    x=(misallocation_no_forecast + misallocation_with_forecast) / 2,
    y=(no_fc["annual_total"] + with_fc["annual_total"]) / 2,
    text=f"<b>Ahorras €{annual_savings:,.0f}/año</b>",
    showarrow=False,
    font=dict(size=15, color=GREEN),
    xshift=100,
)

fig_sens.update_layout(
    xaxis_title="Error de personal (%)",
    yaxis_title="Desperdicio anual (€)",
    template="plotly_white",
    height=450,
    font=dict(size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=14)),
    margin=dict(t=60),
)
st.plotly_chart(fig_sens, use_container_width=True)

# ---------------------------------------------------------------------------
# 7 ▸ CONCLUSIÓN + CTA
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center; padding: 2rem 1rem;">
        <h2>En resumen</h2>
        <p style="font-size:1.15rem; max-width:700px; margin:0 auto; color:#333; line-height:1.6;">
            Un almacén que mueve <b>{units_per_week:,} unidades/semana</b> sin un pronóstico de demanda
            desperdicia aproximadamente <b style="color:{RED};">€{no_fc['annual_total']:,.0f}/año</b> en
            operarios ociosos, horas extra y penalizaciones SLA.<br><br>
            Un pronóstico con <b>{accuracy}% de precisión</b> reduce eso a
            <b style="color:{GREEN};">€{with_fc['annual_total']:,.0f}/año</b> —
            ahorrándote <b style="color:{GREEN};">€{annual_savings:,.0f}</b> cada año.
        </p>
        <p style="margin-top:1.5rem; font-size:1.05rem;">
            <b>La solución no es más gente. Es mejor información.</b>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown(
    "Desarrollado por [HireRobots](https://www.hirrobots.com) — "
    "convirtiendo la planificación reactiva en planificación inteligente con pronóstico de demanda."
)
