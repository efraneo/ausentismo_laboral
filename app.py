"""Aplicación principal - Dashboard de Ausentismo Laboral SST."""
import streamlit as st
from auth.session import init_session, is_logged_in, is_admin, current_user, logout
from database.seed import ensure_admin_user
from pages.login import render_login
from pages.dashboard import render_dashboard
from pages.ausentismo import render_ausentismo
from pages.permisos import render_permisos
from pages.trabajadores import render_trabajadores
from pages.emo import render_emo
from pages.admin import render_admin

st.set_page_config(
    page_title="Dashboard Ausentismo SST",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main():
    init_session()
    ensure_admin_user()

    # No logueado → pantalla de login/registro
    if not is_logged_in():
        render_login()
        return

    # Sidebar
    with st.sidebar:
        u = current_user()
        st.markdown(f"### 👤 {u['nombre']}")
        st.caption(f"👤 Usuario: {u['usuario']}")
        st.caption(f"🎯 Perfil: {u['perfil'].title()}")
        st.caption(f"💼 Cargo: {u.get('cargo','-')}")
        st.caption(f"🔢 Ingresos: {u.get('ingresos_sistema',0)}")
        st.caption(f"⏰ Caducidad: {u.get('caducidad','Indefinido')}")
        st.divider()

        menu = ["📊 Dashboard", "📋 Ausentismo", "📝 Permisos", "👥 Trabajadores"]
        if is_admin():
            menu += ["🩺 EMO", "⚙️ Administración"]
        choice = st.radio("Navegación", menu)
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
            st.rerun()

    # Routing
    if choice == "📊 Dashboard":
        render_dashboard()
    elif choice == "📋 Ausentismo":
        render_ausentismo()
    elif choice == "📝 Permisos":
        render_permisos()
    elif choice == "👥 Trabajadores":
        render_trabajadores()
    elif choice == "🩺 EMO":
        render_emo()
    elif choice == "⚙️ Administración":
        render_admin()


if __name__ == "__main__":
    main()
