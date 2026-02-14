import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config & constants
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="3PL Staffing Cost Calculator · HireRobots",
    page_icon="📦",
    layout="wide",
)

RED = "#E74C3C"
RED_LIGHT = "rgba(231,76,60,0.12)"
GREEN = "#27AE60"
GREEN_LIGHT = "rgba(39,174,96,0.12)"
GREY = "#95A5A6"

# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------
TRANSLATIONS = {
    "es": {
        "lang_label": "🌐 Idioma / Language",
        "page_title": "📦 ¿Cuánto te cuesta una mala planificación de personal?",
        "page_subtitle": (
            "Ajusta los números en la barra lateral para que coincidan con tu operación. "
            "Descubre exactamente cuánto dinero pierdes sin un pronóstico de demanda — "
            "y cuánto ahorras con uno."
        ),
        "sidebar_warehouse": "Tu Almacén",
        "units_per_week": "Unidades movidas por semana",
        "units_per_week_help": "Total de unidades (picks, packs, envíos) que tu almacén maneja semanalmente.",
        "units_per_worker": "Unidades que maneja un operario por semana",
        "units_per_worker_help": "Productividad media de un operario de almacén a tiempo completo.",
        "sidebar_labor": "Costes Laborales",
        "hourly_rate": "Salario por hora (€)",
        "hours_per_week": "Horas por semana",
        "overtime_mult": "Multiplicador de horas extra",
        "overtime_mult_help": "Ej: 1.25 significa que las horas extra cuestan un 25% más que las normales.",
        "sidebar_accuracy": "Precisión del Staffing",
        "error_no_fc": "Error de personal SIN pronóstico (%)",
        "error_no_fc_help": "Cuánto se desvía tu plantilla de la necesidad real en una semana típica, sin pronóstico de demanda.",
        "error_with_fc": "Error de personal CON pronóstico (%)",
        "error_with_fc_help": "Cuánto se desvía tu plantilla cuando usas un buen pronóstico de demanda.",
        "sidebar_penalties": "Penalizaciones",
        "sla_penalty": "Penalización SLA por semana incumplida (€)",
        "sla_penalty_help": "Coste medio de penalización cuando no cumples objetivos por falta de personal.",
        "banner_with_forecast": "Con un pronóstico de demanda ahorras",
        "banner_per_year": "/ año",
        "banner_monthly": "Son <b>€{monthly}</b> cada mes que vuelven a tu margen.",
        "context_text": (
            'Tu almacén mueve <b>{units_per_week} unidades/semana</b>. '
            'Eso requiere aproximadamente <b>{workers:.0f} operarios</b>. '
            'Sin un pronóstico, el personal se desvía ~<b>{misalloc}%</b> — '
            'eso son <b>{over:.0f} operarios de más</b> en semanas flojas '
            'y <b>{under:.0f} operarios de menos</b> en semanas pico.'
        ),
        "where_money_goes": "¿A dónde se va el dinero?",
        "no_forecast": "❌ Sin Pronóstico",
        "with_forecast": "✅ Con Pronóstico ({accuracy}% de precisión)",
        "staff_error": "Error de personal: <b>{pct}%</b>",
        "workers_over": '<b>{n:.0f}</b> operarios de más en semanas flojas',
        "per_month_wasted": "/mes desperdiciados",
        "workers_under": '<b>{n:.0f}</b> operarios de menos en semanas pico → horas extra a {mult}×',
        "per_month_extra": "/mes extra",
        "sla_penalties": "Penalizaciones SLA",
        "per_month": "/mes",
        "annual_waste_total": "Desperdicio anual total:",
        "bar_title": "Desglose Anual de Costes: Antes vs Después del Pronóstico",
        "bar_explainer": (
            "Cada barra muestra de dónde viene el desperdicio laboral. "
            "La <b style='color:#E74C3C'>barra roja</b> es tu coste hoy sin pronóstico. "
            "La <b style='color:#27AE60'>barra verde</b> es tu coste con un pronóstico de demanda. "
            "La diferencia entre ambas es dinero que te quedas."
        ),
        "bar_cat_idle": "Operarios ociosos<br>(sobredotación)",
        "bar_cat_overtime": "Primas de<br>horas extra",
        "bar_cat_sla": "Penalizaciones<br>SLA",
        "bar_legend_no_fc": "Sin Pronóstico",
        "bar_legend_with_fc": "Con Pronóstico",
        "bar_yaxis": "Coste Anual (€)",
        "sim_title": "Cómo se ve un año típico — Semana a semana",
        "sim_explainer": (
            "Esta simulación muestra 52 semanas de planificación de personal. "
            "La <b>línea negra discontinua</b> es cuántos operarios realmente necesitabas. "
            "La <b style='color:#E74C3C'>línea roja</b> es lo que programarías sin pronóstico (adivinando). "
            "La <b style='color:#27AE60'>línea verde</b> es lo que programarías con un pronóstico. "
            "Cada hueco entre las líneas es dinero perdido."
        ),
        "sim_waste_no_fc": "Desperdicio (sin pronóstico)",
        "sim_waste_with_fc": "Desperdicio (con pronóstico)",
        "sim_actual": "Operarios realmente necesarios",
        "sim_sched_no_fc": "Programados — sin pronóstico",
        "sim_sched_with_fc": "Programados — con pronóstico",
        "sim_xaxis": "Semana del año",
        "sim_yaxis": "Número de operarios",
        "sens_title": "¿Cuánto importa la precisión del pronóstico?",
        "sens_explainer": (
            "Este gráfico muestra cómo cambia tu desperdicio anual a medida que mejora la precisión del personal. "
            "Cuanto más a la derecha estés, peores son tus estimaciones — y más dinero pierdes. "
            "Los dos puntos muestran dónde estás <b>hoy</b> (sin pronóstico) y dónde <b>podrías estar</b>."
        ),
        "sens_today": "  Hoy: €{val}",
        "sens_with_fc": "  Con pronóstico: €{val}",
        "sens_no_fc_legend": "Sin pronóstico",
        "sens_with_fc_legend": "Con pronóstico",
        "sens_arrow": "<b>Ahorras €{val}/año</b>",
        "sens_xaxis": "Error de personal (%)",
        "sens_yaxis": "Desperdicio anual (€)",
        "conclusion_title": "En resumen",
        "conclusion_body": (
            'Un almacén que mueve <b>{units_per_week} unidades/semana</b> sin un pronóstico de demanda '
            'desperdicia aproximadamente <b style="color:{red};">€{waste}/año</b> en '
            'operarios ociosos, horas extra y penalizaciones SLA.<br><br>'
            'Un pronóstico con <b>{accuracy}% de precisión</b> reduce eso a '
            '<b style="color:{green};">€{reduced}/año</b> — '
            'ahorrándote <b style="color:{green};">€{savings}</b> cada año.'
        ),
        "conclusion_cta": "<b>La solución no es más gente. Es mejor información.</b>",
        "footer": (
            "Desarrollado por [HireRobots](https://www.hirrobots.com) — "
            "convirtiendo la planificación reactiva en planificación inteligente con pronóstico de demanda."
        ),
    },
    "en": {
        "lang_label": "🌐 Idioma / Language",
        "page_title": "📦 How much does poor staffing planning cost you?",
        "page_subtitle": (
            "Adjust the numbers in the sidebar to match your operation. "
            "Discover exactly how much money you lose without a demand forecast — "
            "and how much you save with one."
        ),
        "sidebar_warehouse": "Your Warehouse",
        "units_per_week": "Units moved per week",
        "units_per_week_help": "Total units (picks, packs, shipments) your warehouse handles weekly.",
        "units_per_worker": "Units handled per worker per week",
        "units_per_worker_help": "Average productivity of a full-time warehouse worker.",
        "sidebar_labor": "Labor Costs",
        "hourly_rate": "Hourly wage (€)",
        "hours_per_week": "Hours per week",
        "overtime_mult": "Overtime multiplier",
        "overtime_mult_help": "E.g.: 1.25 means overtime costs 25% more than regular hours.",
        "sidebar_accuracy": "Staffing Accuracy",
        "error_no_fc": "Staffing error WITHOUT forecast (%)",
        "error_no_fc_help": "How much your staffing deviates from actual need in a typical week, without a demand forecast.",
        "error_with_fc": "Staffing error WITH forecast (%)",
        "error_with_fc_help": "How much your staffing deviates when using a good demand forecast.",
        "sidebar_penalties": "Penalties",
        "sla_penalty": "SLA penalty per missed week (€)",
        "sla_penalty_help": "Average penalty cost when you miss targets due to understaffing.",
        "banner_with_forecast": "With a demand forecast you save",
        "banner_per_year": "/ year",
        "banner_monthly": "That's <b>€{monthly}</b> every month back into your margin.",
        "context_text": (
            'Your warehouse moves <b>{units_per_week} units/week</b>. '
            'That requires roughly <b>{workers:.0f} workers</b>. '
            'Without a forecast, staffing deviates ~<b>{misalloc}%</b> — '
            "that's <b>{over:.0f} extra workers</b> in slow weeks "
            'and <b>{under:.0f} too few</b> in peak weeks.'
        ),
        "where_money_goes": "Where does the money go?",
        "no_forecast": "❌ Without Forecast",
        "with_forecast": "✅ With Forecast ({accuracy}% accuracy)",
        "staff_error": "Staffing error: <b>{pct}%</b>",
        "workers_over": '<b>{n:.0f}</b> extra workers in slow weeks',
        "per_month_wasted": "/mo wasted",
        "workers_under": '<b>{n:.0f}</b> too few in peak weeks → overtime at {mult}×',
        "per_month_extra": "/mo extra",
        "sla_penalties": "SLA Penalties",
        "per_month": "/mo",
        "annual_waste_total": "Total annual waste:",
        "bar_title": "Annual Cost Breakdown: Before vs After Forecast",
        "bar_explainer": (
            "Each bar shows where labor waste comes from. "
            "The <b style='color:#E74C3C'>red bar</b> is your cost today without a forecast. "
            "The <b style='color:#27AE60'>green bar</b> is your cost with a demand forecast. "
            "The difference is money you keep."
        ),
        "bar_cat_idle": "Idle workers<br>(overstaffing)",
        "bar_cat_overtime": "Overtime<br>premiums",
        "bar_cat_sla": "SLA<br>Penalties",
        "bar_legend_no_fc": "Without Forecast",
        "bar_legend_with_fc": "With Forecast",
        "bar_yaxis": "Annual Cost (€)",
        "sim_title": "What a typical year looks like — Week by week",
        "sim_explainer": (
            "This simulation shows 52 weeks of staffing planning. "
            "The <b>dashed black line</b> is how many workers you actually needed. "
            "The <b style='color:#E74C3C'>red line</b> is what you'd schedule without a forecast (guessing). "
            "The <b style='color:#27AE60'>green line</b> is what you'd schedule with a forecast. "
            "Every gap between the lines is money lost."
        ),
        "sim_waste_no_fc": "Waste (without forecast)",
        "sim_waste_with_fc": "Waste (with forecast)",
        "sim_actual": "Workers actually needed",
        "sim_sched_no_fc": "Scheduled — without forecast",
        "sim_sched_with_fc": "Scheduled — with forecast",
        "sim_xaxis": "Week of year",
        "sim_yaxis": "Number of workers",
        "sens_title": "How much does forecast accuracy matter?",
        "sens_explainer": (
            "This chart shows how your annual waste changes as staffing accuracy improves. "
            "The further right you are, the worse your estimates — and the more money you lose. "
            "The two dots show where you are <b>today</b> (no forecast) and where you <b>could be</b>."
        ),
        "sens_today": "  Today: €{val}",
        "sens_with_fc": "  With forecast: €{val}",
        "sens_no_fc_legend": "Without forecast",
        "sens_with_fc_legend": "With forecast",
        "sens_arrow": "<b>You save €{val}/year</b>",
        "sens_xaxis": "Staffing error (%)",
        "sens_yaxis": "Annual waste (€)",
        "conclusion_title": "In summary",
        "conclusion_body": (
            'A warehouse moving <b>{units_per_week} units/week</b> without a demand forecast '
            'wastes roughly <b style="color:{red};">€{waste}/year</b> on '
            'idle workers, overtime, and SLA penalties.<br><br>'
            'A forecast with <b>{accuracy}% accuracy</b> reduces that to '
            '<b style="color:{green};">€{reduced}/year</b> — '
            'saving you <b style="color:{green};">€{savings}</b> every year.'
        ),
        "conclusion_cta": "<b>The solution isn't more people. It's better information.</b>",
        "footer": (
            "Built by [HireRobots](https://www.hirrobots.com) — "
            "turning reactive planning into smart planning with demand forecasting."
        ),
    },
}

# ---------------------------------------------------------------------------
# Language selector (top of sidebar)
# ---------------------------------------------------------------------------
lang_code = st.sidebar.selectbox(
    "🌐 Idioma / Language",
    options=["es", "en"],
    format_func=lambda c: "Español" if c == "es" else "English",
)
t = TRANSLATIONS[lang_code]

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
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
# Header
# ---------------------------------------------------------------------------
st.title(t["page_title"])
st.markdown(t["page_subtitle"])

# ---------------------------------------------------------------------------
# Sidebar — inputs
# ---------------------------------------------------------------------------
st.sidebar.header(t["sidebar_warehouse"])
units_per_week = st.sidebar.number_input(
    t["units_per_week"],
    min_value=1_000, max_value=500_000, value=30_000, step=1_000,
    help=t["units_per_week_help"],
)
units_per_worker_per_week = st.sidebar.number_input(
    t["units_per_worker"],
    min_value=100, max_value=5_000, value=600, step=50,
    help=t["units_per_worker_help"],
)

st.sidebar.header(t["sidebar_labor"])
hourly_rate = st.sidebar.number_input(
    t["hourly_rate"], min_value=5.0, max_value=50.0, value=12.50, step=0.50,
)
hours_per_week = st.sidebar.number_input(
    t["hours_per_week"], min_value=20, max_value=60, value=40, step=1,
)
overtime_multiplier = st.sidebar.number_input(
    t["overtime_mult"],
    min_value=1.0, max_value=3.0, value=1.25, step=0.05,
    help=t["overtime_mult_help"],
)

st.sidebar.header(t["sidebar_accuracy"])
misallocation_no_forecast = st.sidebar.slider(
    t["error_no_fc"], 10, 50, 20, 1, help=t["error_no_fc_help"],
)
misallocation_with_forecast = st.sidebar.slider(
    t["error_with_fc"], 0, 20, 5, 1, help=t["error_with_fc_help"],
)

st.sidebar.header(t["sidebar_penalties"])
sla_penalty_per_miss = st.sidebar.number_input(
    t["sla_penalty"],
    min_value=0, max_value=50_000, value=500, step=100,
    help=t["sla_penalty_help"],
)

# ---------------------------------------------------------------------------
# Calculations
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
# 1 — Savings banner
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="savings-banner">
        <p>{t["banner_with_forecast"]}</p>
        <h1>€{annual_savings:,.0f} {t["banner_per_year"]}</h1>
        <p>{t["banner_monthly"].format(monthly=f"{annual_savings / 12:,.0f}")}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 2 — Plain-language context
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="explainer">
        {t["context_text"].format(
            units_per_week=f"{units_per_week:,}",
            workers=required_workers,
            misalloc=misallocation_no_forecast,
            over=no_fc["workers_over"],
            under=no_fc["workers_under"],
        )}
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# 3 — Side-by-side scenario cards
# ---------------------------------------------------------------------------
st.markdown(f"### {t['where_money_goes']}")

col_bad, col_good = st.columns(2)

with col_bad:
    st.markdown(
        f"""
        <div class="scenario-card scenario-bad">
            <h3>{t["no_forecast"]}</h3>
            <p class="detail">{t["staff_error"].format(pct=misallocation_no_forecast)}</p>
            <p class="detail">
                🧑‍🤝‍🧑 {t["workers_over"].format(n=no_fc["workers_over"])}
                → <span class="big-num" style="color:{RED};">€{no_fc['monthly_overstaffing']:,.0f}</span>{t["per_month_wasted"]}
            </p>
            <p class="detail">
                🔥 {t["workers_under"].format(n=no_fc["workers_under"], mult=overtime_multiplier)}
                → <span class="big-num" style="color:{RED};">€{no_fc['monthly_overtime']:,.0f}</span>{t["per_month_extra"]}
            </p>
            <p class="detail">
                ⚠️ {t["sla_penalties"]}
                → <span class="big-num" style="color:{RED};">€{no_fc['monthly_sla']:,.0f}</span>{t["per_month"]}
            </p>
            <hr>
            <p class="detail" style="font-size:1.1rem;">
                {t["annual_waste_total"]} <span class="big-num" style="color:{RED};">€{no_fc['annual_total']:,.0f}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

accuracy = 100 - misallocation_with_forecast

with col_good:
    st.markdown(
        f"""
        <div class="scenario-card scenario-good">
            <h3>{t["with_forecast"].format(accuracy=accuracy)}</h3>
            <p class="detail">{t["staff_error"].format(pct=misallocation_with_forecast)}</p>
            <p class="detail">
                🧑‍🤝‍🧑 {t["workers_over"].format(n=with_fc["workers_over"])}
                → <span class="big-num" style="color:{GREEN};">€{with_fc['monthly_overstaffing']:,.0f}</span>{t["per_month"]}
            </p>
            <p class="detail">
                🔥 {t["workers_under"].format(n=with_fc["workers_under"], mult=overtime_multiplier)}
                → <span class="big-num" style="color:{GREEN};">€{with_fc['monthly_overtime']:,.0f}</span>{t["per_month"]}
            </p>
            <p class="detail">
                ⚠️ {t["sla_penalties"]}
                → <span class="big-num" style="color:{GREEN};">€{with_fc['monthly_sla']:,.0f}</span>{t["per_month"]}
            </p>
            <hr>
            <p class="detail" style="font-size:1.1rem;">
                {t["annual_waste_total"]} <span class="big-num" style="color:{GREEN};">€{with_fc['annual_total']:,.0f}</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# 4 — Bar chart: cost breakdown
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"### {t['bar_title']}")
st.markdown(
    f'<div class="explainer">{t["bar_explainer"]}</div>',
    unsafe_allow_html=True,
)

categories = [t["bar_cat_idle"], t["bar_cat_overtime"], t["bar_cat_sla"]]
no_fc_vals = [no_fc["annual_overstaffing"], no_fc["annual_overtime"], no_fc["annual_sla"]]
with_fc_vals = [with_fc["annual_overstaffing"], with_fc["annual_overtime"], with_fc["annual_sla"]]

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name=t["bar_legend_no_fc"],
    x=categories, y=no_fc_vals,
    marker_color=RED,
    text=[f"€{v:,.0f}" for v in no_fc_vals],
    textposition="outside",
    textfont=dict(size=14, color=RED),
))
fig_bar.add_trace(go.Bar(
    name=t["bar_legend_with_fc"],
    x=categories, y=with_fc_vals,
    marker_color=GREEN,
    text=[f"€{v:,.0f}" for v in with_fc_vals],
    textposition="outside",
    textfont=dict(size=14, color=GREEN),
))
fig_bar.update_layout(
    barmode="group",
    yaxis_title=t["bar_yaxis"],
    template="plotly_white",
    height=420,
    font=dict(size=14),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=14)),
    margin=dict(t=60),
)
st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------------------------
# 5 — Weekly simulation (52 weeks)
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"### {t['sim_title']}")
st.markdown(
    f'<div class="explainer">{t["sim_explainer"]}</div>',
    unsafe_allow_html=True,
)

np.random.seed(42)
demand = np.random.normal(loc=units_per_week, scale=units_per_week * 0.15, size=52)
demand = np.clip(demand, units_per_week * 0.5, units_per_week * 1.5)
actual_needed = demand / units_per_worker_per_week

no_fc_staff = np.full(52, required_workers) + np.random.normal(
    0, required_workers * misallocation_no_forecast / 200, 52
)
no_fc_staff = np.clip(no_fc_staff, 1, None)

with_fc_staff = actual_needed + np.random.normal(
    0, required_workers * misallocation_with_forecast / 200, 52
)
with_fc_staff = np.clip(with_fc_staff, 1, None)

weeks = np.arange(1, 53)

fig_sim = go.Figure()

fig_sim.add_trace(go.Scatter(
    x=np.concatenate([weeks, weeks[::-1]]),
    y=np.concatenate([np.maximum(actual_needed, no_fc_staff),
                      np.minimum(actual_needed, no_fc_staff)[::-1]]),
    fill="toself",
    fillcolor=RED_LIGHT,
    line=dict(width=0),
    name=t["sim_waste_no_fc"],
    hoverinfo="skip",
))

fig_sim.add_trace(go.Scatter(
    x=np.concatenate([weeks, weeks[::-1]]),
    y=np.concatenate([np.maximum(actual_needed, with_fc_staff),
                      np.minimum(actual_needed, with_fc_staff)[::-1]]),
    fill="toself",
    fillcolor=GREEN_LIGHT,
    line=dict(width=0),
    name=t["sim_waste_with_fc"],
    hoverinfo="skip",
))

fig_sim.add_trace(go.Scatter(
    x=weeks, y=actual_needed, mode="lines",
    name=t["sim_actual"],
    line=dict(color="black", width=2, dash="dash"),
))
fig_sim.add_trace(go.Scatter(
    x=weeks, y=no_fc_staff, mode="lines",
    name=t["sim_sched_no_fc"],
    line=dict(color=RED, width=2),
))
fig_sim.add_trace(go.Scatter(
    x=weeks, y=with_fc_staff, mode="lines",
    name=t["sim_sched_with_fc"],
    line=dict(color=GREEN, width=2),
))

fig_sim.update_layout(
    xaxis_title=t["sim_xaxis"],
    yaxis_title=t["sim_yaxis"],
    template="plotly_white",
    height=450,
    font=dict(size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=13)),
    margin=dict(t=60),
)
st.plotly_chart(fig_sim, use_container_width=True)

# ---------------------------------------------------------------------------
# 6 — Sensitivity chart
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(f"### {t['sens_title']}")
st.markdown(
    f'<div class="explainer">{t["sens_explainer"]}</div>',
    unsafe_allow_html=True,
)

misalloc_range = np.arange(0, 51, 1)
annual_totals = [scenario_costs(m)["annual_total"] for m in misalloc_range]

fig_sens = go.Figure()

fig_sens.add_trace(go.Scatter(
    x=misalloc_range, y=annual_totals,
    mode="lines",
    line=dict(color=GREY, width=2),
    fill="tozeroy",
    fillcolor="rgba(149,165,166,0.10)",
    showlegend=False,
))

fig_sens.add_trace(go.Scatter(
    x=[misallocation_no_forecast],
    y=[no_fc["annual_total"]],
    mode="markers+text",
    marker=dict(size=18, color=RED, symbol="circle"),
    text=[t["sens_today"].format(val=f"{no_fc['annual_total']:,.0f}")],
    textposition="middle right",
    textfont=dict(size=14, color=RED),
    name=t["sens_no_fc_legend"],
))
fig_sens.add_trace(go.Scatter(
    x=[misallocation_with_forecast],
    y=[with_fc["annual_total"]],
    mode="markers+text",
    marker=dict(size=18, color=GREEN, symbol="circle"),
    text=[t["sens_with_fc"].format(val=f"{with_fc['annual_total']:,.0f}")],
    textposition="middle right",
    textfont=dict(size=14, color=GREEN),
    name=t["sens_with_fc_legend"],
))

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
    text=t["sens_arrow"].format(val=f"{annual_savings:,.0f}"),
    showarrow=False,
    font=dict(size=15, color=GREEN),
    xshift=100,
)

fig_sens.update_layout(
    xaxis_title=t["sens_xaxis"],
    yaxis_title=t["sens_yaxis"],
    template="plotly_white",
    height=450,
    font=dict(size=13),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=14)),
    margin=dict(t=60),
)
st.plotly_chart(fig_sens, use_container_width=True)

# ---------------------------------------------------------------------------
# 7 — Conclusion + CTA
# ---------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center; padding: 2rem 1rem;">
        <h2>{t["conclusion_title"]}</h2>
        <p style="font-size:1.15rem; max-width:700px; margin:0 auto; color:#333; line-height:1.6;">
            {t["conclusion_body"].format(
                units_per_week=f"{units_per_week:,}",
                red=RED,
                waste=f"{no_fc['annual_total']:,.0f}",
                accuracy=accuracy,
                green=GREEN,
                reduced=f"{with_fc['annual_total']:,.0f}",
                savings=f"{annual_savings:,.0f}",
            )}
        </p>
        <p style="margin-top:1.5rem; font-size:1.05rem;">
            {t["conclusion_cta"]}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown(t["footer"])
