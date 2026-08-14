"""Dashboard principal con KPIs, gráficos e IA."""
import streamlit as st
import pandas as pd
from utils.helpers import fetch_ausentismo, fetch_permisos, fetch_trabajadores
from components.charts import (chart_dias_por_mes, chart_ausentismo_por_tipo,
                                chart_ausentismo_por_proceso, chart_top_diagnosticos,
                                chart_accidentes_por_dia_semana, chart_permisos_por_mes,
                                chart_permisos_por_tipo)
from components.metrics import (kpi_total_dias_perdidos, kpi_total_casos,
                                 kpi_total_accidentes, kpi_costo_total,
                                 kpi_vinculados, kpi_desvinculados, kpi_emo_pendientes)
from components.ai_assistant import render_ai_assistant
from auth.session import is_admin

def render_dashboard():
    st.markdown("## 📊 Dashboard de Ausentismo Laboral")
    st.caption("Vista general de indicadores de SST - 2026")

    df_aus = fetch_ausentismo()
    df_per = fetch_permisos()
    df_tra = fetch_trabajadores()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Días Perdidos", f"{kpi_total_dias_perdidos(df_aus):,}")
    c2.metric("📋 Casos de Ausentismo", f"{kpi_total_casos(df_aus):,}")
    c3.metric("⚠️ Accidentes Laborales", f"{kpi_total_accidentes(df_aus):,}")
    c4.metric("💰 Costo Estimado", f"${kpi_costo_total(df_aus):,.0f}")

    st.markdown("---")
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("👥 Vinculados", f"{kpi_vinculados(df_tra):,}")
    c6.metric("🚪 Desvinculados", f"{kpi_desvinculados(df_tra):,}")
    c7.metric("📝 Permisos Laborales", f"{len(df_per):,}")
    c8.metric("🩺 EMO Pendientes", f"{kpi_emo_pendientes(df_tra):,}")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a: st.plotly_chart(chart_dias_por_mes(df_aus), use_container_width=True)
    with col_b: st.plotly_chart(chart_ausentismo_por_tipo(df_aus), use_container_width=True)

    st.plotly_chart(chart_ausentismo_por_proceso(df_aus), use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c: st.plotly_chart(chart_top_diagnosticos(df_aus), use_container_width=True)
    with col_d: st.plotly_chart(chart_accidentes_por_dia_semana(df_aus), use_container_width=True)

    st.markdown("---")
    st.markdown("### 📋 Permisos Laborales")
    col_e, col_f = st.columns(2)
    with col_e: st.plotly_chart(chart_permisos_por_mes(df_per), use_container_width=True)
    with col_f: st.plotly_chart(chart_permisos_por_tipo(df_per), use_container_width=True)

    # --- Asistente IA (Solo Admin) ---
    if is_admin():
        st.markdown("---")
        render_ai_assistant(df_aus, df_tra)
