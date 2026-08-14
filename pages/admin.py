"""Panel de administración: usuarios, carga de datos."""
import streamlit as st
from auth.session import is_admin
from auth.authentication import aprobar_usuario, rechazar_usuario
from utils.helpers import fetch_usuarios
from utils.data_loader import (cargar_excel_ausentismo, cargar_excel_base_datos,
                                cargar_excel_permisos)


def render_admin():
    st.markdown("## ⚙️ Panel de Administración")
    if not is_admin():
        st.error("⛔ Acceso solo para administradores.")
        return

    tab_users, tab_load = st.tabs(["👥 Aprobación de Usuarios", "📤 Carga de Datos"])

    # --- Aprobación de usuarios ---
    with tab_users:
        df = fetch_usuarios()
        if df.empty:
            st.info("No hay usuarios.")
            return
        pendientes = df[df["estado"] == "pendiente_aprobacion"]
        st.markdown(f"### 🕒 Usuarios esperando aprobación ({len(pendientes)})")
        if pendientes.empty:
            st.success("No hay usuarios pendientes.")
        else:
            for _, u in pendientes.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 1, 1])
                    c1.markdown(f"**{u['nombre']}**  ")
                    c1.caption(f"Usuario: {u['usuario']} · Correo: {u.get('correo','-')} · "
                               f"Identificación: {u.get('identificacion','-')} · Cargo: {u.get('cargo','-')}")
                    if c2.button("✅ Aprobar", key=f"ap_{u['id']}"):
                        aprobar_usuario(u["id"])
                        st.success(f"{u['nombre']} aprobado.")
                        st.rerun()
                    if c3.button("❌ Rechazar", key=f"rc_{u['id']}"):
                        rechazar_usuario(u["id"])
                        st.warning(f"{u['nombre']} rechazado.")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Todos los usuarios")
        show = ["usuario","nombre","correo","identificacion","cargo","perfil","estado",
                "ingresos_sistema","ultimo_ingreso","caducidad"]
        show = [c for c in show if c in df.columns]
        st.dataframe(df[show], use_container_width=True, hide_index=True)

    # --- Carga de datos ---
    with tab_load:
        st.markdown("### 📤 Cargar datos desde Excel")
        st.info("Sube los archivos Excel para sincronizar con la base de datos.")

        st.markdown("#### 📄 Archivo: REGISTRO DE AUSENTISMO 2026.xlsx")
        f1 = st.file_uploader("Ausentismo + Base de Datos", type=["xlsx"], key="f1")
        col1, col2 = st.columns(2)
        if col1.button("Cargar hoja AUSENTISMO") and f1:
            with st.spinner("Cargando..."):
                n = cargar_excel_ausentismo(f1)
                st.success(f"✅ {n} registros de ausentismo cargados.")
        if col2.button("Cargar hoja BASE DATOS") and f1:
            with st.spinner("Cargando..."):
                n = cargar_excel_base_datos(f1)
                st.success(f"✅ {n} trabajadores cargados/actualizados.")

        st.markdown("---")
        st.markdown("#### 📄 Archivo: REGISTRO DE PERMISO LABORAL 2026.xlsx")
        f2 = st.file_uploader("Permisos laborales", type=["xlsx"], key="f2")
        if st.button("Cargar hoja Formato") and f2:
            with st.spinner("Cargando..."):
                n = cargar_excel_permisos(f2)
                st.success(f"✅ {n} permisos laborales cargados.")
