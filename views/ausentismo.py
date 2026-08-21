"""Página detallada de Ausentismo."""
import streamlit as st
import pandas as pd
from utils.helpers import fetch_ausentismo
from components.charts import (chart_dias_por_mes, chart_ausentismo_por_tipo,
                                chart_ausentismo_por_proceso, chart_top_diagnosticos,
                                chart_top_ausentismo_trabajadores)

def render_ausentismo():
    st.markdown("## 📋 Registro de Ausentismo Laboral")
    df = fetch_ausentismo()
    if df.empty:
        st.warning("No hay datos de ausentismo cargados.")
        return

    with st.expander("🔍 Filtros", expanded=False):
        col1, col2, col3 = st.columns(3)
        opciones_mes = df["mes"].dropna().unique().tolist() if "mes" in df else []
        mes_sel = col1.multiselect("Mes", options=opciones_mes)
        opciones_proceso = df["proceso"].dropna().unique().tolist() if "proceso" in df else []
        proceso_sel = col2.multiselect("Proceso", options=opciones_proceso)
        opciones_asunto = df["asunto"].dropna().unique().tolist() if "asunto" in df else []
        asunto_sel = col3.multiselect("Tipo", options=opciones_asunto)

        dff = df.copy()
        if mes_sel: dff = dff[dff["mes"].isin(mes_sel)]
        if proceso_sel: dff = dff[dff["proceso"].isin(proceso_sel)]
        if asunto_sel: dff = dff[dff["asunto"].isin(asunto_sel)]

    cols = ["cedula","apellidos_nombres","cargo","proceso","asunto","tipo_incapacidad",
            "fecha_inicial","fecha_final","dias_perdidos","mes","costo_incapacidad",
            "codigo_cie10","diagnostico"]
    show_cols = [c for c in cols if c in dff.columns]
    st.dataframe(dff[show_cols], use_container_width=True, height=400, hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 Visualizaciones")
    
    # Top 10 Ausentes
    st.plotly_chart(chart_top_ausentismo_trabajadores(dff), use_container_width=True)
    
    # Tabla detallada del Top 10
    st.markdown("#### 📝 Detalle del Top 10 Ausentes (Motivos y Fechas)")
    if "apellidos_nombres" in dff.columns and "dias_perdidos" in dff.columns:
        top_nombres = dff.groupby("apellidos_nombres")["dias_perdidos"].sum().nlargest(10).index.tolist()
        dff_top = dff[dff["apellidos_nombres"].isin(top_nombres)].sort_values("dias_perdidos", ascending=False)
        cols_det = ["apellidos_nombres", "dia_semana", "fecha_inicial", "fecha_final", "dias_perdidos", "asunto", "diagnostico"]
        cols_det = [c for c in cols_det if c in dff_top.columns]
        st.dataframe(dff_top[cols_det], use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(chart_dias_por_mes(dff), use_container_width=True)
    with c2: st.plotly_chart(chart_ausentismo_por_tipo(dff), use_container_width=True)
    
    st.plotly_chart(chart_ausentismo_por_proceso(dff), use_container_width=True)
    st.plotly_chart(chart_top_diagnosticos(dff, top=15), use_container_width=True)

    st.download_button("⬇️ Descargar CSV", dff.to_csv(index=False).encode(),
                       file_name="ausentismo.csv", mime="text/csv")
