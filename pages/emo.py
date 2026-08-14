"""Página de gestión de EMO (solo administrador)."""
import streamlit as st
from utils.helpers import fetch_trabajadores, update_emo
from auth.session import is_admin
from datetime import date


def render_emo():
    st.markdown("## 🩺 Exámenes Médicos Ocupacionales (EMO)")
    if not is_admin():
        st.error("⛔ Solo el administrador puede gestionar EMO.")
        return

    df = fetch_trabajadores()
    if df.empty:
        st.warning("No hay trabajadores.")
        return

    st.markdown("### Resumen de EMO")
    c1, c2, c3 = st.columns(3)
    c1.metric("EMO Ingreso Pendientes",
              int((df["emo_ingreso"].astype(str).str.lower() == "pendiente").sum()) if "emo_ingreso" in df else 0)
    c2.metric("EMO Periódico Pendientes",
              int((df["emo_periodico"].astype(str).str.lower() == "pendiente").sum()) if "emo_periodico" in df else 0)
    c3.metric("EMO Retiro Pendientes",
              int((df["emo_retiro"].astype(str).str.lower() == "pendiente").sum()) if "emo_retiro" in df else 0)

    st.markdown("---")
    st.markdown("### 📝 Actualizar EMO de un trabajador")

    with st.form("emo_form"):
        df_sel = df.copy()
        df_sel["label"] = df_sel["apellidos_nombres"].astype(str) + " — CC: " + df_sel["identificacion"].astype(str)
        sel = st.selectbox("Trabajador", df_sel["label"].tolist())

        col1, col2, col3 = st.columns(3)

        def emo_input(col, label, campo):
            col.markdown(f"**{label}**")
            actual = df_sel[df_sel["label"] == sel][campo].iloc[0] if campo in df_sel.columns else "Pendiente"
            op = col.radio("Estado actual: " + str(actual), ["Pendiente", "Realizado"], key=f"op_{campo}")
            if op == "Realizado":
                return col.date_input("Fecha EMO", value=date.today(), key=f"date_{campo}").strftime("%d/%m/%Y")
            return "Pendiente"

        v_ingreso = emo_input(col1, "EMO de Ingreso", "emo_ingreso")
        v_periodico = emo_input(col2, "EMO Periódico", "emo_periodico")
        v_retiro = emo_input(col3, "EMO de Retiro", "emo_retiro")

        if st.form_submit_button("💾 Guardar EMO", use_container_width=True, type="primary"):
            idx = df_sel.index[df_sel["label"] == sel][0]
            tid = df_sel.loc[idx, "id"]
            update_emo(tid, "emo_ingreso", v_ingreso)
            update_emo(tid, "emo_periodico", v_periodico)
            update_emo(tid, "emo_retiro", v_retiro)
            st.success("✅ EMO actualizado correctamente.")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Tabla general de EMO")
    show = ["identificacion","apellidos_nombres","cargo","area","estado",
            "emo_ingreso","emo_periodico","emo_retiro"]
    show = [c for c in show if c in df.columns]
    st.dataframe(df[show], use_container_width=True, height=500, hide_index=True)
