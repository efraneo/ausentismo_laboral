"""Página de Permisos Laborales."""
import streamlit as st
import pandas as pd
from utils.helpers import fetch_permisos
from components.charts import (chart_permisos_por_mes, chart_permisos_por_tipo, 
                               chart_top_permisos_trabajadores)

def render_permisos():
    st.markdown("## 📋 Registro de Permisos Laborales")
    df = fetch_permisos()
    if df.empty:
        st.warning("No hay permisos laborales cargados.")
        return

    with st.expander("🔍 Filtros"):
        col1, col2 = st.columns(2)
        opciones_mes = df["mes"].dropna().unique().tolist() if "mes" in df else []
        mes_sel = col1.multiselect("Mes", options=opciones_mes)
        opciones_tipo = df["tipo_permiso"].dropna().unique().tolist() if "tipo_permiso" in df else []
        tipo_sel = col2.multiselect("Tipo de Permiso", options=opciones_tipo)

        dff = df.copy()
        if mes_sel: dff = dff[dff["mes"].isin(mes_sel)]
        if tipo_sel: dff = dff[dff["tipo_permiso"].isin(tipo_sel)]

    cols = ["cedula","apellidos_nombres","cargo","area","asunto","tipo_permiso",
            "fecha_inicial","fecha_final","hora_inicio","hora_final","horas","mes"]
    show_cols = [c for c in cols if c in dff.columns]
    st.dataframe(dff[show_cols], use_container_width=True, height=400, hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 Visualizaciones")
    
    # Top 10 Permisos
    st.plotly_chart(chart_top_permisos_trabajadores(dff), use_container_width=True)
    
    # Tabla detallada Top 10
    st.markdown("#### 📝 Detalle del Top 10 (Fechas y Motivos)")
    if "apellidos_nombres" in dff.columns:
        dff["horas_num"] = pd.to_numeric(dff.get("horas", 0), errors='coerce').fillna(0)
        top_nombres = dff.groupby("apellidos_nombres")["horas_num"].sum().nlargest(10).index.tolist()
        dff_top = dff[dff["apellidos_nombres"].isin(top_nombres)].sort_values("horas_num", ascending=False)
        cols_det = ["apellidos_nombres", "tipo_permiso", "fecha_inicial", "hora_inicio", "hora_final", "horas", "asunto"]
        cols_det = [c for c in cols_det if c in dff_top.columns]
        st.dataframe(dff_top[cols_det], use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(chart_permisos_por_mes(dff), use_container_width=True)
    with c2: st.plotly_chart(chart_permisos_por_tipo(dff), use_container_width=True)

    st.download_button("⬇️ Descargar CSV", dff.to_csv(index=False).encode(),
                       file_name="permisos.csv", mime="text/csv")
