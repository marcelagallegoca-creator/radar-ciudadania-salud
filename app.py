"""
🏥 Radar Ciudadano — Contratación en Salud (SECOP)
Dashboard de vigilancia ciudadana para contratación pública en el sector salud colombiano.

Módulos:
1. Scorecard Municipal ("¿Cómo va mi departamento?")
2. Top Contratos Atípicos del Mes
3. Concentración de Proveedores
4. Gasto vs. Resultados en Salud
5. Precios de Referencia
6. Fragmentación de Contratos
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_generator import (
    generar_datos_departamento,
    calcular_concentracion_proveedores,
    detectar_fragmentacion,
    DEPARTAMENTOS,
)

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Radar Ciudadano — Salud SECOP",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# ESTILOS CSS
# ============================================================

st.markdown("""
<style>
    /* Tipografía general */
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1200px;
    }
    
    /* Header principal */
    .header-ciudadano {
        background: linear-gradient(135deg, #1B3A5C 0%, #2E75B6 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .header-ciudadano h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .header-ciudadano p {
        margin: 0.3rem 0 0 0;
        opacity: 0.85;
        font-size: 0.95rem;
    }
    
    /* Disclaimer */
    .disclaimer-box {
        background: #FFF8E1;
        border-left: 4px solid #F9A825;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 1.5rem;
        font-size: 0.85rem;
        color: #5D4037;
    }
    
    /* Scorecard */
    .scorecard {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .scorecard .valor {
        font-size: 2rem;
        font-weight: 800;
        color: #1B3A5C;
        line-height: 1.1;
    }
    .scorecard .etiqueta {
        font-size: 0.8rem;
        color: #757575;
        margin-top: 0.3rem;
    }
    
    /* Semáforo de riesgo */
    .riesgo-alto { color: #C62828; font-weight: 700; }
    .riesgo-medio { color: #EF6C00; font-weight: 700; }
    .riesgo-bajo { color: #2E7D32; font-weight: 700; }
    
    /* Módulo header */
    .modulo-header {
        border-left: 4px solid #2E75B6;
        padding-left: 0.8rem;
        margin: 1.5rem 0 1rem 0;
    }
    .modulo-header h2 {
        margin: 0;
        font-size: 1.3rem;
        color: #1B3A5C;
    }
    .modulo-header p {
        margin: 0.2rem 0 0 0;
        font-size: 0.85rem;
        color: #757575;
    }
    
    /* Compartir */
    .compartir-box {
        background: #E3F2FD;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    /* Fiabilidad */
    .fiabilidad-alta { background: #E8F5E9; border-left: 3px solid #4CAF50; padding: 0.5rem 0.8rem; border-radius: 0 6px 6px 0; font-size: 0.8rem; }
    .fiabilidad-media { background: #FFF8E1; border-left: 3px solid #FFC107; padding: 0.5rem 0.8rem; border-radius: 0 6px 6px 0; font-size: 0.8rem; }
    .fiabilidad-baja { background: #FFEBEE; border-left: 3px solid #F44336; padding: 0.5rem 0.8rem; border-radius: 0 6px 6px 0; font-size: 0.8rem; }
    
    /* Ocultar menú hamburguesa default */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ============================================================
# CARGA DE DATOS
# ============================================================

@st.cache_data
def cargar_datos():
    df, df_salud, df_salud_temporal = generar_datos_departamento()
    df_concentracion = calcular_concentracion_proveedores(df)
    df_fragmentacion = detectar_fragmentacion(df)
    return df, df_salud, df_salud_temporal, df_concentracion, df_fragmentacion

df, df_salud, df_salud_temporal, df_concentracion, df_fragmentacion = cargar_datos()


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def formato_moneda(valor):
    """Formatea valor en COP de forma legible."""
    if valor >= 1_000_000_000:
        return f"${valor/1_000_000_000:,.1f}B"
    elif valor >= 1_000_000:
        return f"${valor/1_000_000:,.0f}M"
    else:
        return f"${valor:,.0f}"


def semaforo_riesgo(nivel):
    """Devuelve emoji + texto coloreado según nivel."""
    if nivel == "Alto":
        return "🔴"
    elif nivel == "Medio":
        return "🟡"
    return "🟢"


def indicador_fiabilidad(itm):
    """Genera indicador de fiabilidad basado en el ITM del departamento."""
    if itm >= 65:
        return "alta", "✅ Fiabilidad alta. Datos consistentes y completos en su mayoría."
    elif itm >= 45:
        return "media", "⚠️ Fiabilidad media. Algunos campos incompletos. Interpretar con cautela."
    else:
        return "baja", "🔻 Fiabilidad baja. Datos con vacíos significativos. Requiere verificación adicional."


def generar_texto_compartir(dep, data_dep):
    """Genera texto plano para compartir en WhatsApp/redes."""
    n_alertas = len(data_dep[data_dep["nivel_riesgo"].isin(["Alto", "Medio"])])
    valor_total = data_dep["valor"].sum()
    texto = (
        f"🏥 Radar Ciudadano — {dep}\n"
        f"📊 {len(data_dep)} contratos de salud analizados\n"
        f"⚠️ {n_alertas} con señales de atipicidad\n"
        f"💰 Valor total: {formato_moneda(valor_total)}\n\n"
        f"ℹ️ Estos datos son señales estadísticas, no acusaciones. "
        f"Un contrato atípico puede tener explicaciones legítimas.\n\n"
        f"🔗 Consulta el dashboard completo en: [URL]"
    )
    return texto


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="header-ciudadano">
    <h1>🏥 Radar Ciudadano — Contratación en Salud</h1>
    <p>Vigilancia ciudadana de la contratación pública en el sector salud colombiano · Datos SECOP II</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer permanente
st.markdown("""
<div class="disclaimer-box">
    <strong>⚠️ Información importante:</strong> Este dashboard identifica <strong>patrones estadísticos atípicos</strong>, 
    no irregularidades confirmadas. Un contrato señalado puede tener explicaciones legítimas 
    (urgencia médica, condiciones geográficas, emergencia sanitaria). La información proviene de datos públicos del SECOP 
    y su uso para acusaciones sin verificación adicional es responsabilidad exclusiva del usuario.
</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR — FILTROS
# ============================================================

with st.sidebar:
    st.markdown("### 🔍 Filtros")
    
    departamento_sel = st.selectbox(
        "Departamento",
        options=["Todos"] + sorted(df["departamento"].unique().tolist()),
        index=0,
    )
    
    nivel_riesgo_sel = st.multiselect(
        "Nivel de riesgo",
        options=["Alto", "Medio", "Bajo"],
        default=["Alto", "Medio", "Bajo"],
    )
    
    modalidad_sel = st.multiselect(
        "Modalidad de contratación",
        options=sorted(df["modalidad"].unique().tolist()),
        default=sorted(df["modalidad"].unique().tolist()),
    )
    
    estado_sel = st.selectbox(
        "Estado del proceso",
        options=["Todos", "En proceso", "Adjudicado"],
        index=0,
        help="En proceso = pre-adjudicación (alerta temprana). Adjudicado = proceso finalizado.",
    )
    
    rango_fechas = st.date_input(
        "Rango de fechas",
        value=(df["fecha_publicacion"].min(), df["fecha_publicacion"].max()),
        min_value=df["fecha_publicacion"].min(),
        max_value=df["fecha_publicacion"].max(),
    )
    
    st.markdown("---")
    st.markdown(
        "📋 **Fuentes:** SECOP II · DNP · "
        "Transparencia por Colombia · DANE"
    )
    st.markdown(
        "📅 **Última actualización:** Datos simulados "
        "para prototipo académico"
    )

# Aplicar filtros (vacío = seleccionar todos)
df_filtrado = df.copy()
if departamento_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["departamento"] == departamento_sel]

# Si el usuario deselecciona todo, se interpreta como "ver todos"
niveles_activos = nivel_riesgo_sel if nivel_riesgo_sel else ["Alto", "Medio", "Bajo"]
modalidades_activas = modalidad_sel if modalidad_sel else sorted(df["modalidad"].unique().tolist())

df_filtrado = df_filtrado[df_filtrado["nivel_riesgo"].isin(niveles_activos)]
df_filtrado = df_filtrado[df_filtrado["modalidad"].isin(modalidades_activas)]
if estado_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado"] == estado_sel]
if len(rango_fechas) == 2:
    df_filtrado = df_filtrado[
        (df_filtrado["fecha_publicacion"].dt.date >= rango_fechas[0])
        & (df_filtrado["fecha_publicacion"].dt.date <= rango_fechas[1])
    ]

# Mensaje si los filtros no devuelven datos
if len(df_filtrado) == 0:
    st.warning(
        "⚠️ No se encontraron contratos con los filtros seleccionados. "
        "Prueba ampliando el rango de fechas o seleccionando otros criterios."
    )
    st.stop()

# Aviso si se restauraron filtros vacíos
if not nivel_riesgo_sel or not modalidad_sel:
    st.info("ℹ️ Se muestran todos los niveles de riesgo y/o modalidades porque no seleccionaste ningún filtro específico.")


# ============================================================
# MÓDULO 1: SCORECARD DEPARTAMENTAL
# ============================================================

st.markdown("""
<div class="modulo-header">
    <h2>📍 ¿Cómo va mi departamento?</h2>
    <p>Resumen ejecutivo de la contratación en salud en tu territorio</p>
</div>
""", unsafe_allow_html=True)

# Cálculos nacionales para comparación
prom_nacional_pct_alto = (
    len(df[df["nivel_riesgo"] == "Alto"]) / max(len(df), 1) * 100
)

if departamento_sel == "Todos":
    st.info("👆 Selecciona un departamento en los filtros para ver su scorecard personalizado.")
    
    # Vista nacional resumida
    n_adjudicado = len(df_filtrado[df_filtrado["estado"] == "Adjudicado"])
    n_en_proceso = len(df_filtrado[df_filtrado["estado"] == "En proceso"])
    valor_adjudicado = df_filtrado[df_filtrado["estado"] == "Adjudicado"]["valor"].sum()
    valor_en_proceso = df_filtrado[df_filtrado["estado"] == "En proceso"]["valor"].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Contratos analizados", f"{len(df_filtrado):,}")
    with col2:
        n_alertas = len(df_filtrado[df_filtrado["nivel_riesgo"] == "Alto"])
        st.metric("Alertas altas", f"{n_alertas}")
    with col3:
        st.metric("Valor adjudicado", formato_moneda(valor_adjudicado))
    with col4:
        st.metric("Valor estimado en proceso", formato_moneda(valor_en_proceso))

else:
    dep_info = DEPARTAMENTOS[departamento_sel]
    dep_data = df_filtrado[df_filtrado["departamento"] == departamento_sel]
    dep_salud = df_salud[df_salud["departamento"] == departamento_sel].iloc[0] if len(df_salud[df_salud["departamento"] == departamento_sel]) > 0 else None
    
    # Indicador de fiabilidad
    nivel_fiab, texto_fiab = indicador_fiabilidad(dep_info["itm"])
    st.markdown(f'<div class="fiabilidad-{nivel_fiab}">{texto_fiab}</div>', unsafe_allow_html=True)
    
    # --- Cambio 1: Comparación vs promedio nacional ---
    pct_alto_dep = len(dep_data[dep_data["nivel_riesgo"] == "Alto"]) / max(len(dep_data), 1) * 100
    diff_vs_nacional = round(pct_alto_dep - prom_nacional_pct_alto, 1)
    
    # --- Cambio 2: Valores por estado ---
    valor_adj = dep_data[dep_data["estado"] == "Adjudicado"]["valor"].sum()
    valor_proc = dep_data[dep_data["estado"] == "En proceso"]["valor"].sum()
    
    # KPIs fila 1: Contratación
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Contratos", f"{len(dep_data):,}")
    with col2:
        n_alto = len(dep_data[dep_data["nivel_riesgo"] == "Alto"])
        if diff_vs_nacional > 0:
            st.metric("Riesgo alto", f"{n_alto}", delta=f"+{diff_vs_nacional:.1f} pp vs. promedio nacional", delta_color="inverse")
        else:
            st.metric("Riesgo alto", f"{n_alto}", delta=f"{diff_vs_nacional:.1f} pp vs. promedio nacional", delta_color="inverse")
    with col3:
        st.metric("💰 Valor adjudicado", formato_moneda(valor_adj))
    with col4:
        st.metric("⏳ Valor estimado en proceso", formato_moneda(valor_proc),
                   help="Procesos en fase pre-adjudicación. Este es el espacio donde la alerta temprana permite actuar.")
    
    # KPIs fila 2: Contexto territorial
    col5, col6 = st.columns(2)
    with col5:
        st.metric("Índ. Desempeño Fiscal", f"{dep_info['idf']}/100",
                   help="Mide la gestión financiera del departamento (DNP). Menor valor = mayor vulnerabilidad fiscal.")
    with col6:
        st.metric("Índ. Transparencia", f"{dep_info['itm']}/100",
                   help="Mide riesgo de corrupción administrativa (Transparencia por Colombia). Menor valor = mayor riesgo.")
    
    # --- Cambio 5: Evolución indicadores de salud vs. gasto ---
    dep_temporal = df_salud_temporal[df_salud_temporal["departamento"] == departamento_sel]
    
    if len(dep_temporal) > 0:
        st.markdown("**📊 Evolución: inversión en salud vs. indicadores del territorio (2023–2025)**")
        st.caption(
            "¿Se traduce el gasto en contratación de salud en mejores indicadores? "
            "Esta comparación no implica causalidad directa — factores externos como "
            "migración, emergencias sanitarias o tiempos de maduración de proyectos "
            "también influyen en los resultados."
        )
        
        indicador_temporal = st.selectbox(
            "Indicador de salud a comparar:",
            options=["cobertura_vacunacion", "mortalidad_infantil_x1000",
                     "camas_x10000_hab", "medicos_x10000_hab"],
            format_func=lambda x: {
                "cobertura_vacunacion": "Cobertura de vacunación (%)",
                "mortalidad_infantil_x1000": "Mortalidad infantil (‰)",
                "camas_x10000_hab": "Camas hospitalarias / 10.000 hab",
                "medicos_x10000_hab": "Médicos / 10.000 hab",
            }[x],
            key="indicador_temporal_m1",
        )
        
        # Gráfico de doble eje
        fig_evol = go.Figure()
        
        # Barras: gasto en salud
        fig_evol.add_trace(go.Bar(
            x=dep_temporal["anio"],
            y=dep_temporal["gasto_salud"],
            name="Gasto en contratación",
            marker_color="#B0BEC5",
            opacity=0.7,
            yaxis="y",
        ))
        
        # Línea: indicador de salud
        nombre_indicador = {
            "cobertura_vacunacion": "Cobertura vacunación (%)",
            "mortalidad_infantil_x1000": "Mortalidad infantil (‰)",
            "camas_x10000_hab": "Camas / 10.000 hab",
            "medicos_x10000_hab": "Médicos / 10.000 hab",
        }[indicador_temporal]
        
        fig_evol.add_trace(go.Scatter(
            x=dep_temporal["anio"],
            y=dep_temporal[indicador_temporal],
            name=nombre_indicador,
            mode="lines+markers",
            line=dict(color="#2E75B6", width=3),
            marker=dict(size=10),
            yaxis="y2",
        ))
        
        fig_evol.update_layout(
            yaxis=dict(title="Gasto en contratación (COP)", side="left", showgrid=False),
            yaxis2=dict(title=nombre_indicador, side="right", overlaying="y", showgrid=True),
            xaxis=dict(title="", tickvals=[2023, 2024, 2025], dtick=1),
            height=350,
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            barmode="group",
        )
        st.plotly_chart(fig_evol, use_container_width=True)
        
        # Narrativa automática
        if len(dep_temporal) >= 3:
            gasto_23 = dep_temporal[dep_temporal["anio"] == 2023]["gasto_salud"].values[0]
            gasto_25 = dep_temporal[dep_temporal["anio"] == 2025]["gasto_salud"].values[0]
            ind_23 = dep_temporal[dep_temporal["anio"] == 2023][indicador_temporal].values[0]
            ind_25 = dep_temporal[dep_temporal["anio"] == 2025][indicador_temporal].values[0]
            
            if gasto_23 > 0:
                cambio_gasto = (gasto_25 - gasto_23) / gasto_23 * 100
                cambio_ind = ind_25 - ind_23
                
                # Interpretar según indicador (mortalidad: menor = mejor)
                mejor_si_sube = indicador_temporal != "mortalidad_infantil_x1000"
                indicador_mejoro = (cambio_ind > 0) if mejor_si_sube else (cambio_ind < 0)
                
                if cambio_gasto > 10 and not indicador_mejoro:
                    st.warning(
                        f"⚠️ Entre 2023 y 2025, el gasto en contratación de salud "
                        f"{'aumentó' if cambio_gasto > 0 else 'disminuyó'} un **{abs(cambio_gasto):.0f}%**, "
                        f"pero el indicador {nombre_indicador.lower()} "
                        f"{'empeoró' if not indicador_mejoro else 'mejoró'} "
                        f"({ind_23} → {ind_25}). Esto no confirma irregularidades — "
                        f"puede deberse a inversiones de largo plazo, factores externos o "
                        f"presiones demográficas."
                    )
                elif cambio_gasto > 10 and indicador_mejoro:
                    st.success(
                        f"✅ Entre 2023 y 2025, el gasto en contratación de salud "
                        f"aumentó un **{abs(cambio_gasto):.0f}%** y el indicador "
                        f"{nombre_indicador.lower()} mejoró ({ind_23} → {ind_25})."
                    )
    
    # Ranking nacional
    dep_rank = df.groupby("departamento").apply(
        lambda x: len(x[x["nivel_riesgo"] == "Alto"]) / max(len(x), 1) * 100
    ).sort_values(ascending=False)
    posicion = list(dep_rank.index).index(departamento_sel) + 1
    total_deps = len(dep_rank)
    
    if posicion <= total_deps * 0.3:
        st.warning(f"⚠️ **{departamento_sel}** está en la posición **{posicion} de {total_deps}** departamentos con mayor proporción de alertas altas a nivel nacional.")
    else:
        st.success(f"✅ **{departamento_sel}** está en la posición **{posicion} de {total_deps}** — por debajo del promedio nacional en proporción de alertas.")
    
    # Botón compartir
    texto_compartir = generar_texto_compartir(departamento_sel, dep_data)
    with st.expander("📤 Compartir esta información"):
        st.code(texto_compartir, language=None)
        st.caption("Copia este texto y compártelo en WhatsApp, redes sociales o correo electrónico.")


st.markdown("---")


# ============================================================
# MÓDULO 2: TOP CONTRATOS ATÍPICOS
# ============================================================

st.markdown("""
<div class="modulo-header">
    <h2>🔎 Contratos con señales de atipicidad</h2>
    <p>Los contratos con mayor score de riesgo. Recuerda: atípico no significa irregular.</p>
</div>
""", unsafe_allow_html=True)

top_n = st.slider("Número de contratos a mostrar", 5, 50, 20, key="top_n")
df_top = df_filtrado.nlargest(top_n, "score_riesgo")

for _, row in df_top.iterrows():
    semaforo = semaforo_riesgo(row["nivel_riesgo"])
    
    with st.expander(
        f"{semaforo} **{row['id_contrato']}** — {row['entidad']} — "
        f"{formato_moneda(row['valor'])} — Score: {row['score_riesgo']}/100"
    ):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"**Departamento:** {row['departamento']}")
            st.markdown(f"**Modalidad:** {row['modalidad']}")
            st.markdown(f"**Objeto:** {row['objeto']}")
        with c2:
            st.markdown(f"**Proveedor:** {row['proveedor']}")
            st.markdown(f"**Oferentes:** {row['num_oferentes']}")
            st.markdown(f"**Duración:** {row['duracion_dias']} días")
        with c3:
            st.markdown(f"**Fecha:** {row['fecha_publicacion'].strftime('%d/%m/%Y')}")
            st.markdown(f"**Precio vs referencia:** {row['ratio_precio']:.1f}x")
            if row["periodo_preelectoral"]:
                st.markdown("🗳️ **Periodo preelectoral**")
            if row["fin_anio_fiscal"]:
                st.markdown("📅 **Fin de año fiscal**")
        
        # Explicación en lenguaje ciudadano
        st.markdown("---")
        st.markdown("**¿Por qué este contrato tiene señales de atipicidad?**")
        razones = []
        if row["ratio_precio"] > 1.5:
            razones.append(f"💰 El valor es **{row['ratio_precio']:.1f} veces** el precio de referencia para contratos similares.")
        if row["num_oferentes"] == 1:
            razones.append("👤 **Solo un oferente** participó en el proceso. No hubo competencia.")
        if row["modalidad"] == "Contratación Directa":
            razones.append("📋 Se usó **contratación directa**, que no requiere convocatoria abierta.")
        if row["periodo_preelectoral"]:
            razones.append("🗳️ Publicado en **periodo preelectoral**, donde históricamente aumenta la contratación atípica.")
        if row["fin_anio_fiscal"]:
            razones.append("📅 Publicado a **fin de año fiscal**, cuando hay presión por ejecutar presupuesto.")
        if row["idf_departamento"] < 50:
            razones.append(f"📉 El departamento tiene un **Índice de Desempeño Fiscal bajo** ({row['idf_departamento']}/100).")
        
        if razones:
            for r in razones:
                st.markdown(r)
        
        # Posibles explicaciones legítimas
        st.markdown("**¿Podría tener explicación legítima?**")
        st.markdown(
            "Sí. Un valor alto puede deberse a: contrato plurianual, zona de difícil acceso, "
            "emergencia sanitaria declarada, o especificaciones técnicas que limitan proveedores. "
            "Esta señal **requiere verificación** antes de sacar conclusiones."
        )


st.markdown("---")


# ============================================================
# MÓDULO 3: CONCENTRACIÓN DE PROVEEDORES
# ============================================================

st.markdown("""
<div class="modulo-header">
    <h2>🏢 ¿Hay competencia real?</h2>
    <p>Mapa de concentración de proveedores: cuando pocos acaparan muchos contratos</p>
</div>
""", unsafe_allow_html=True)

# Recalcular concentración con datos filtrados si hay filtro de departamento
if departamento_sel != "Todos":
    df_conc_mostrar = df_concentracion[df_concentracion["departamento"] == departamento_sel]
else:
    df_conc_mostrar = df_concentracion.copy()

if len(df_conc_mostrar) > 0:
    col_mapa, col_tabla = st.columns([3, 2])
    
    with col_mapa:
        # Gráfico de barras de concentración por departamento
        df_conc_sorted = df_conc_mostrar.sort_values("top3_concentracion_pct", ascending=True).tail(15)
        
        fig_conc = go.Figure()
        fig_conc.add_trace(go.Bar(
            y=df_conc_sorted["departamento"],
            x=df_conc_sorted["top3_concentracion_pct"],
            orientation="h",
            marker=dict(
                color=df_conc_sorted["top3_concentracion_pct"],
                colorscale=[[0, "#4CAF50"], [0.5, "#FFC107"], [1, "#F44336"]],
                cmin=30,
                cmax=100,
            ),
            text=[f"{v:.0f}%" for v in df_conc_sorted["top3_concentracion_pct"]],
            textposition="auto",
        ))
        fig_conc.update_layout(
            title="% del valor acaparado por los 3 principales proveedores",
            xaxis_title="Concentración (%)",
            yaxis_title="",
            height=450,
            margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig_conc, use_container_width=True)
    
    with col_tabla:
        st.markdown("**¿Qué significa esto?**")
        st.markdown(
            "Cuando **pocos proveedores** acaparan la mayoría de los contratos de salud "
            "en un departamento, la competencia es baja. Esto puede indicar:\n"
        )
        st.markdown("- Barreras de entrada para nuevos proveedores")
        st.markdown("- Posible favorecimiento en adjudicaciones")
        st.markdown("- Mercado con pocos oferentes reales")
        st.markdown(
            "\nUn departamento sano debería tener un valor **por debajo del 60%**. "
            "Por encima del **80%** es una señal que merece atención."
        )
        
        # Top proveedores si hay departamento seleccionado
        if departamento_sel != "Todos":
            st.markdown(f"**Top proveedores en {departamento_sel}:**")
            dep_provs = df_filtrado.groupby("proveedor").agg(
                contratos=("id_contrato", "count"),
                valor=("valor", "sum"),
            ).sort_values("valor", ascending=False).head(5)
            dep_provs["valor_fmt"] = dep_provs["valor"].apply(formato_moneda)
            st.dataframe(
                dep_provs[["contratos", "valor_fmt"]].rename(
                    columns={"contratos": "Contratos", "valor_fmt": "Valor total"}
                ),
                use_container_width=True,
            )

st.markdown("---")


# ============================================================
# MÓDULO 4: GASTO VS RESULTADOS EN SALUD
# ============================================================

st.markdown("""
<div class="modulo-header">
    <h2>💊 Dinero vs. Resultados</h2>
    <p>¿Se traduce la inversión en salud en mejores indicadores? Los departamentos que gastan mucho pero tienen malos resultados merecen atención.</p>
</div>
""", unsafe_allow_html=True)

# Calcular gasto per cápita por departamento
gasto_dep = df.groupby("departamento")["valor"].sum().reset_index()
gasto_dep.columns = ["departamento", "gasto_total"]
gasto_dep["poblacion"] = gasto_dep["departamento"].map(lambda d: DEPARTAMENTOS[d]["poblacion"])
gasto_dep["gasto_per_capita"] = gasto_dep["gasto_total"] / gasto_dep["poblacion"]

# Merge con datos de salud
df_gasto_salud = gasto_dep.merge(df_salud, on="departamento")
df_gasto_salud["idf"] = df_gasto_salud["departamento"].map(lambda d: DEPARTAMENTOS[d]["idf"])

indicador_eje_y = st.selectbox(
    "Indicador de resultado en salud:",
    options=[
        "cobertura_vacunacion",
        "mortalidad_infantil_x1000",
        "camas_x10000_hab",
        "medicos_x10000_hab",
    ],
    format_func=lambda x: {
        "cobertura_vacunacion": "Cobertura de vacunación (%)",
        "mortalidad_infantil_x1000": "Mortalidad infantil (por 1.000 nacidos vivos)",
        "camas_x10000_hab": "Camas hospitalarias por 10.000 habitantes",
        "medicos_x10000_hab": "Médicos por 10.000 habitantes",
    }[x],
    key="indicador_salud",
)

# Invertir eje Y para mortalidad (menor = mejor)
invertir = indicador_eje_y == "mortalidad_infantil_x1000"

fig_scatter = px.scatter(
    df_gasto_salud,
    x="gasto_per_capita",
    y=indicador_eje_y,
    size="gasto_total",
    color="idf",
    color_continuous_scale=["#F44336", "#FFC107", "#4CAF50"],
    hover_name="departamento",
    hover_data={
        "gasto_per_capita": ":.0f",
        indicador_eje_y: ":.1f",
        "gasto_total": ":.2s",
        "idf": ":.1f",
    },
    labels={
        "gasto_per_capita": "Gasto en salud per cápita (COP)",
        indicador_eje_y: {
            "cobertura_vacunacion": "Cobertura vacunación (%)",
            "mortalidad_infantil_x1000": "Mortalidad infantil (‰)",
            "camas_x10000_hab": "Camas / 10.000 hab",
            "medicos_x10000_hab": "Médicos / 10.000 hab",
        }[indicador_eje_y],
        "idf": "Índ. Desempeño Fiscal",
        "gasto_total": "Gasto total",
    },
)

# Añadir cuadrantes
median_x = df_gasto_salud["gasto_per_capita"].median()
median_y = df_gasto_salud[indicador_eje_y].median()

fig_scatter.add_hline(y=median_y, line_dash="dash", line_color="gray", opacity=0.5)
fig_scatter.add_vline(x=median_x, line_dash="dash", line_color="gray", opacity=0.5)

# Anotaciones de cuadrantes
if invertir:
    fig_scatter.add_annotation(x=median_x * 1.8, y=median_y * 0.5, text="⚠️ Alto gasto +<br>Baja mortalidad", showarrow=False, font=dict(size=10, color="green"))
    fig_scatter.add_annotation(x=median_x * 1.8, y=median_y * 1.5, text="🔴 Alto gasto +<br>Alta mortalidad", showarrow=False, font=dict(size=10, color="red"))
else:
    fig_scatter.add_annotation(x=median_x * 1.8, y=median_y * 1.3, text="✅ Alto gasto +<br>Buenos resultados", showarrow=False, font=dict(size=10, color="green"))
    fig_scatter.add_annotation(x=median_x * 1.8, y=median_y * 0.7, text="🔴 Alto gasto +<br>Malos resultados", showarrow=False, font=dict(size=10, color="red"))

fig_scatter.update_layout(
    height=500,
    plot_bgcolor="white",
    margin=dict(l=10, r=10, t=30, b=10),
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.caption(
    "Cada burbuja es un departamento. El tamaño representa el gasto total y el color el Índice de Desempeño Fiscal (verde = alto, rojo = bajo). "
    "Los departamentos en el cuadrante de alto gasto con malos resultados merecen una mirada más detenida."
)


st.markdown("---")


# ============================================================
# MÓDULO 5: PRECIOS DE REFERENCIA
# ============================================================

st.markdown("""
<div class="modulo-header">
    <h2>💲 ¿Estamos pagando de más?</h2>
    <p>Comparación del valor pagado vs. precio de referencia para contratos similares</p>
</div>
""", unsafe_allow_html=True)

# Filtrar contratos con ratio alto
df_precios = df_filtrado[["id_contrato", "departamento", "entidad", "objeto", "valor",
                           "precio_referencia", "ratio_precio", "modalidad",
                           "score_riesgo", "nivel_riesgo"]].copy()
df_precios = df_precios.sort_values("ratio_precio", ascending=False)

col_dist, col_detalle = st.columns([2, 3])

with col_dist:
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=df_precios["ratio_precio"],
        nbinsx=30,
        marker=dict(
            color=np.where(df_precios["ratio_precio"] > 1.5, "#F44336", 
                          np.where(df_precios["ratio_precio"] > 1.2, "#FFC107", "#4CAF50")),
        ),
        opacity=0.8,
    ))
    fig_hist.add_vline(x=1.0, line_dash="solid", line_color="green",
                       annotation_text="Precio de referencia", annotation_position="top")
    fig_hist.add_vline(x=1.5, line_dash="dash", line_color="red",
                       annotation_text="50% sobre referencia", annotation_position="top")
    fig_hist.update_layout(
        title="Distribución: valor pagado vs. referencia",
        xaxis_title="Ratio (valor / precio referencia)",
        yaxis_title="Número de contratos",
        height=380,
        plot_bgcolor="white",
        margin=dict(l=10, r=10, t=50, b=10),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with col_detalle:
    st.markdown("**Contratos con mayor sobreprecio respecto a referencia:**")
    
    umbral_precio = st.slider("Mostrar contratos con ratio mayor a:", 1.0, 3.0, 1.5, 0.1, key="umbral_precio")
    
    df_sobreprecio = df_precios[df_precios["ratio_precio"] >= umbral_precio].head(15)
    
    if len(df_sobreprecio) > 0:
        for _, row in df_sobreprecio.iterrows():
            st.markdown(
                f"{semaforo_riesgo(row['nivel_riesgo'])} **{row['id_contrato']}** — "
                f"{row['entidad']} — {row['objeto']}\n\n"
                f"Pagado: **{formato_moneda(row['valor'])}** · "
                f"Referencia: {formato_moneda(row['precio_referencia'])} · "
                f"**{row['ratio_precio']:.1f}x**"
            )
    else:
        st.info("No hay contratos por encima del umbral seleccionado.")

st.caption(
    "El precio de referencia se calcula a partir de la mediana de contratos similares "
    "(mismo objeto, misma modalidad). Un ratio de 2.0x significa que el contrato costó "
    "el doble de lo esperado. Esto NO confirma irregularidad — puede haber razones "
    "legítimas como especificaciones técnicas particulares o condiciones geográficas."
)


st.markdown("---")


# ============================================================
# MÓDULO 6: FRAGMENTACIÓN DE CONTRATOS
# ============================================================

st.markdown("""
<div class="modulo-header">
    <h2>🧩 Posible fragmentación de contratos</h2>
    <p>Cuando una entidad divide una compra grande en múltiples contratos pequeños para evitar procesos competitivos</p>
</div>
""", unsafe_allow_html=True)

if departamento_sel != "Todos":
    df_frag_mostrar = df_fragmentacion[
        df_fragmentacion["entidad"].str.contains(departamento_sel, case=False)
    ]
else:
    df_frag_mostrar = df_fragmentacion.copy()

if len(df_frag_mostrar) > 0:
    st.markdown(f"**{len(df_frag_mostrar)} casos detectados** donde la misma entidad adjudicó 3 o más contratos "
                f"al mismo proveedor en el mismo mes.")
    
    for _, row in df_frag_mostrar.head(10).iterrows():
        with st.expander(
            f"🧩 {row['entidad']} → {row['proveedor']} · "
            f"{row['n_contratos']} contratos · {row['mes']} · "
            f"Valor total: {formato_moneda(row['valor_total'])}"
        ):
            st.markdown(f"**Entidad:** {row['entidad']}")
            st.markdown(f"**Proveedor:** {row['proveedor']}")
            st.markdown(f"**Mes:** {row['mes']}")
            st.markdown(f"**Contratos en el mes:** {row['n_contratos']}")
            st.markdown(f"**Valor acumulado:** {formato_moneda(row['valor_total'])}")
            st.markdown(f"**Modalidades usadas:** {', '.join(row['modalidades'])}")
            st.markdown(f"**Objetos contratados:** {', '.join(row['objetos'][:3])}")
            
            st.markdown("---")
            st.markdown("**¿Por qué es una señal?**")
            st.markdown(
                "Dividir una compra en múltiples contratos de menor cuantía puede ser una "
                "estrategia para evitar los umbrales que exigen licitación pública o selección "
                "abreviada. Esta práctica está documentada como una de las 73 banderas rojas "
                "de la Open Contracting Partnership."
            )
            st.markdown("**¿Podría tener explicación legítima?**")
            st.markdown(
                "Sí. Puede tratarse de entregas programadas, lotes distintos de suministros, "
                "o necesidades que surgieron en momentos diferentes del mismo mes."
            )
else:
    st.info("No se detectaron casos de posible fragmentación con los filtros actuales.")


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #9E9E9E; font-size: 0.8rem; padding: 1rem 0;">
    <strong>Radar Ciudadano — Contratación en Salud (SECOP)</strong><br>
    Proyecto académico · Especialización en Inteligencia Artificial · Universidad Javeriana · 2026<br>
    Los datos presentados son señales estadísticas derivadas de datos públicos. No constituyen acusaciones.<br>
    Este dashboard es un prototipo con datos simulados para validación de concepto.
</div>
""", unsafe_allow_html=True)
