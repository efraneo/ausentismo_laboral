"""Página de Permisos Laborales."""
import streamlit as st
from utils.helpers import fetch_permisos
from components.charts import chart_permisos_por_mes, chart_permisos_por_tipo


def render_permisos():
    st.markdown("## 📋 Registro de Permisos Laborales")
    df = fetch_permisos()
    if df.empty:
        st.warning("No hay permisos laborales cargados.")
        return

    with st.expander("🔍 Filtros"):
        col1, col2 = st.columns(2)
        mes_sel = col1.multiselect("Mes", options=df["mes"].dropna().unique().tolist() if "mes" in df else [])
        tipo_sel = col2.multiselect("Tipo de Permiso", options=df["tipo_permiso"].dropna().unique().tolist() if "tipo_permiso" in df else [])

    dff = df.copy()
    if mes_sel:
        dff = dff[dff["mes"].isin(mes_sel)]
    if tipo_sel:
        dff = dff[dff["tipo_permiso"].isin(tipo_sel)]

    cols = ["cedula","apellidos_nombres","cargo","area","asunto","tipo_permiso",
            "fecha_inicial","fecha_final","hora_inicio","hora_final","horas","mes"]
    show_cols = [c for c in cols if c in dff.columns]
    st.dataframe(dff[show_cols], use_container_width=True, height=500, hide_index=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(chart_permisos_por_mes(dff), use_container_width=True)
    with c2:
        st.plotly_chart(chart_permisos_por_tipo(dff), use_container_width=True)

    st.download_button("⬇️ Descargar CSV", dff.to_csv(index=False).encode(),
                       file_name="permisos.csv", mime="text/csv")
