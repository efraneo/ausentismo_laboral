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
            st.info("No hay usuarios registrados aún.")
        else:
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
        st.info("ℹ️ Sube el archivo de Excel. El sistema leerá automáticamente las pestañas internas (AUSENTISMO, BASE DATOS, Formato).")

        st.markdown("#### 📄 Archivo 1: REGISTRO DE AUSENTISMO 2026.xlsx")
        st.caption("Este archivo contiene la hoja 'AUSENTISMO' y la hoja 'BASE DATOS' (Trabajadores).")
        f1 = st.file_uploader("Arrastra o examina el archivo de Ausentismo", type=["xlsx"], key="f1")
        
        col1, col2 = st.columns(2)
        if col1.button("1️⃣ Cargar hoja AUSENTISMO", use_container_width=True, type="primary"):
            if f1 is not None:
                with st.spinner("Procesando ausentismo..."):
                    n = cargar_excel_ausentismo(f1)
                    st.success(f"✅ {n} registros de ausentismo cargados correctamente.")
            else:
                st.warning("⚠️ Sube el archivo primero.")
                
        if col2.button("2️⃣ Cargar hoja BASE DATOS (Trabajadores)", use_container_width=True, type="primary"):
            if f1 is not None:
                with st.spinner("Procesando trabajadores..."):
                    n = cargar_excel_base_datos(f1)
                    st.success(f"✅ {n} trabajadores cargados/actualizados correctamente.")
            else:
                st.warning("⚠️ Sube el archivo primero.")

        st.markdown("---")
        st.markdown("#### 📄 Archivo 2: REGISTRO DE PERMISO LABORAL 2026.xlsx")
        st.caption("Este archivo contiene la hoja 'Formato' con los permisos laborales.")
        f2 = st.file_uploader("Arrastra o examina el archivo de Permisos", type=["xlsx"], key="f2")
        
        if st.button("3️⃣ Cargar hoja de Permisos", use_container_width=True, type="primary"):
            if f2 is not None:
                with st.spinner("Procesando permisos..."):
                    n = cargar_excel_permisos(f2)
                    st.success(f"✅ {n} permisos laborales cargados correctamente.")
            else:
                st.warning("⚠️ Sube el archivo primero.")
