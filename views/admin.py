"""Panel de administración: usuarios, carga de datos."""
import streamlit as st
import pandas as pd
from auth.session import is_admin
from auth.authentication import aprobar_usuario, rechazar_usuario
from utils.helpers import fetch_usuarios, fetch_trabajadores
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
            st.info("No hay usuarios registrados.")
        else:
            pendientes = df[df["estado"] == "pendiente_aprobacion"]
            st.markdown(f"### 🕒 Usuarios esperando aprobación ({len(pendientes)})")
            if pendientes.empty:
                st.success("✅ No hay usuarios pendientes de aprobación.")
            else:
                for _, u in pendientes.iterrows():
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([4, 1, 1])
                        c1.markdown(f"**{u['nombre']}**")
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
        st.info("ℹ️ Sube los archivos Excel. El sistema leerá automáticamente las pestañas internas.")

        # ========== ARCHIVO 1: AUSENTISMO ==========
        st.markdown("#### 📄 Archivo: REGISTRO DE AUSENTISMO 2026.xlsx")
        st.caption("Este archivo contiene la hoja 'AUSENTISMO' y la hoja 'BASE DATOS' (Trabajadores).")

        f1 = st.file_uploader(
            "👉 Arrastra o examina el archivo de Ausentismo aquí",
            type=["xlsx"],
            key="uploader_ausentismo"
        )

        if f1 is not None:
            st.success(f"📎 Archivo cargado: {f1.name}")

            col1, col2 = st.columns(2)
            btn_aus = col1.button("1️⃣ Cargar hoja AUSENTISMO", use_container_width=True, type="primary")
            btn_tra = col2.button("2️⃣ Cargar hoja BASE DATOS (Trabajadores)", use_container_width=True, type="primary")

            if btn_aus:
                with st.spinner("Procesando ausentismo..."):
                    f1.seek(0)
                    n, msg = cargar_excel_ausentismo(f1)
                    st.success(msg)

            if btn_tra:
                with st.spinner("Procesando trabajadores..."):
                    f1.seek(0)
                    n, msg = cargar_excel_base_datos(f1)
                    st.success(msg)

        st.markdown("---")

        # ========== ARCHIVO 2: PERMISOS ==========
        st.markdown("#### 📄 Archivo: REGISTRO DE PERMISO LABORAL 2026.xlsx")
        st.caption("Este archivo contiene la hoja 'Formato' con los permisos laborales.")

        f2 = st.file_uploader(
            "👉 Arrastra o examina el archivo de Permisos aquí",
            type=["xlsx"],
            key="uploader_permisos"
        )

        if f2 is not None:
            st.success(f"📎 Archivo cargado: {f2.name}")

            if st.button("3️⃣ Cargar hoja de Permisos", use_container_width=True, type="primary"):
                with st.spinner("Procesando permisos..."):
                    f2.seek(0)
                    n, msg = cargar_excel_permisos(f2)
                    st.success(msg)

        st.markdown("---")

        # ========== TABLA DE TRABAJADORES CARGADOS ==========
        st.markdown("### 📋 Trabajadores cargados en la base de datos")
        st.caption("Tabla con el estado actual de cada trabajador. Si no tiene estado, se asignó 'Vinculado' automáticamente.")

        try:
            df_tra = fetch_trabajadores()
            if df_tra.empty:
                st.warning("⚠️ No hay trabajadores cargados. Sube un archivo y presiona el botón 'Cargar hoja BASE DATOS'.")
            else:
                # Mostrar columnas principales
                show_cols = ["identificacion", "apellidos_nombres", "cargo", "area",
                           "fecha_ingreso", "eps", "estado", "emo_ingreso",
                           "emo_periodico", "emo_retiro"]
                show_cols = [c for c in show_cols if c in df_tra.columns]

                # Resaltar el estado con colores
                st.dataframe(
                    df_tra[show_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=500
                )

                # Mostrar resumen de estados
                st.markdown("---")
                c1, c2, c3 = st.columns(3)
                if "estado" in df_tra.columns:
                    vinculados = len(df_tra[df_tra["estado"] == "Vinculado"])
                    desvinculados = len(df_tra[df_tra["estado"] == "Desvinculado"])
                    total = len(df_tra)
                    c1.metric("👥 Total Trabajadores", total)
                    c2.metric("✅ Vinculados", vinculados)
                    c3.metric("🚪 Desvinculados", desvinculados)

                # Descargar CSV
                st.markdown("---")
                csv = df_tra.to_csv(index=False).encode()
                st.download_button(
                    "⬇️ Descargar tabla de trabajadores (CSV)",
                    csv,
                    file_name="trabajadores.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error al cargar la tabla de trabajadores: {e}")
