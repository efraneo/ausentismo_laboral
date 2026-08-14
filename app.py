"""Aplicación principal - Dashboard de Ausentismo Laboral SST."""
import streamlit as st
from auth.session import init_session, is_logged_in, is_admin, current_user, logout
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
    # Inicializar variables de sesión
    init_session()

    # Si no está logueado, mostrar pantalla de login/registro
    if not is_logged_in():
        render_login()
        return

    # Barra lateral (Sidebar)
    with st.sidebar:
        u = current_user()
        st.markdown(f"### 👤 {u['nombre']}")
        st.caption(f"👤 Usuario: `{u['usuario']}`")
        st.caption(f"🎯 Perfil: **{u['perfil'].title()}**")
        st.caption(f"💼 Cargo: {u.get('cargo', 'No definido')}")
        
        # Mostrar contador de ingresos solo si existe en el objeto del usuario
        if 'ingresos_sistema' in u:
            st.caption(f"🔢 Ingresos al sistema: {u.get('ingresos_sistema', 0)}")
            
        st.caption(f"⏰ Caducidad: {u.get('caducidad', 'Indefinido')}")
        st.divider()

        # Menú de navegación
        menu = ["📊 Dashboard", "📋 Ausentismo", "📝 Permisos", "👥 Trabajadores"]
        
        # Si es administrador, mostrar opciones extra
        if is_admin():
            menu += ["🩺 EMO", "⚙️ Administración"]
            
        choice = st.radio("🗂️ Navegación", menu)
        st.divider()
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="primary"):
            logout()
            st.rerun()

    # Enrutamiento de páginas
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
