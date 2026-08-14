"""Página detallada de Ausentismo."""
import streamlit as st
import pandas as pd
from utils.helpers import fetch_ausentismo
from components.charts import (chart_dias_por_mes, chart_ausentismo_por_tipo,
                                chart_ausentismo_por_proceso, chart_top_diagnosticos)


def render_ausentismo():
    st.markdown("## 📋 Registro de Ausentismo Laboral")
    df = fetch_ausentismo()
    if df.empty:
        st.warning("No hay datos de ausentismo cargados.")
        return

    # Filtros
    with st.expander("🔍 Filtros", expanded=False):
        col1, col2, col3 = st.columns(3)
        mes_sel = col1.multiselect("Mes", options=df["mes"].dropna().unique().tolist() if "mes" in df else [])
        proceso_sel = col2.multiselect("Proceso", options=df["proceso"].dropna().unique().tolist() if "proceso" in df else [])
        asunto_sel = col3.multiselect("Tipo", options=df["asunto"].dropna().unique().tolist() if "asunto" in df else [])

        dff = df.copy()
        if mes_sel:
            dff = dff[dff["mes"].isin(mes_sel)]
        if proceso_sel:
            dff = dff[dff["proceso"].isin(proceso_sel)]
        if asunto_sel:
            dff = dff[dff["asunto"].isin(asunto_sel)]

    cols = ["cedula","apellidos_nombres","cargo","proceso","asunto","tipo_incapacidad",
            "fecha_inicial","fecha_final","dias_perdidos","mes","costo_incapacidad",
            "codigo_cie10","diagnostico"]
    show_cols = [c for c in cols if c in dff.columns]
    st.dataframe(dff[show_cols], use_container_width=True, height=500, hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 Visualizaciones")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_dias_por_mes(dff), use_container_width=True)
    with c2:
        st.plotly_chart(chart_ausentismo_por_tipo(dff), use_container_width=True)
    st.plotly_chart(chart_ausentismo_por_proceso(dff), use_container_width=True)
    st.plotly_chart(chart_top_diagnosticos(dff, top=15), use_container_width=True)

    # Descarga CSV
    st.download_button("⬇️ Descargar CSV", dff.to_csv(index=False).encode(),
                       file_name="ausentismo.csv", mime="text/csv")
