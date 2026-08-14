"""Página de trabajadores con estado Vinculado/Desvinculado."""
import streamlit as st
from utils.helpers import fetch_trabajadores, update_trabajador_estado
from auth.session import is_admin


def render_trabajadores():
    st.markdown("## 👥 Base de Datos de Trabajadores")
    estado_filtro = st.selectbox("Filtrar por estado", ["Todos", "Vinculado", "Desvinculado"])
    df = fetch_trabajadores(estado=None if estado_filtro == "Todos" else estado_filtro)
    if df.empty:
        st.warning("No hay trabajadores cargados.")
        return

    # Búsqueda
    search = st.text_input("🔎 Buscar por nombre, cédula o cargo").strip().lower()
    if search:
        mask = df.apply(lambda r: search in str(r.values).lower(), axis=1)
        df = df[mask]

    cols = ["identificacion","apellidos_nombres","cargo","area","fecha_ingreso",
            "eps","afp","sexo","edad","estado","emo_ingreso","emo_periodico","emo_retiro"]
    show_cols = [c for c in cols if c in df.columns]
    st.dataframe(df[show_cols], use_container_width=True, height=600, hide_index=True)

    # Admin puede cambiar estado
    if is_admin():
        st.markdown("---")
        st.markdown("### ⚙️ Cambiar estado de trabajador")
        with st.form("cambiar_estado"):
            opciones = df[["id","apellidos_nombres","estado"]].copy()
            opciones["label"] = opciones["apellidos_nombres"].astype(str) + " — " + opciones["estado"].astype(str)
            sel = st.selectbox("Trabajador", opciones["label"].tolist())
            nuevo_estado = st.selectbox("Nuevo estado", ["Vinculado","Desvinculado"])
            if st.form_submit_button("Actualizar"):
                idx = opciones.index[opciones["label"] == sel][0]
                tid = opciones.loc[idx, "id"]
                update_trabajador_estado(tid, nuevo_estado)
                st.success(f"Estado actualizado a '{nuevo_estado}'.")
                st.rerun()
