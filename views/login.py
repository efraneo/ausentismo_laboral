"""Página de Login."""
import streamlit as st
from auth.authentication import login
from auth.session import set_user, init_session
from views.register import render_register  # <--- CAMBIA 'pages' POR 'views'

def render_login():
    init_session()
    st.markdown("""
    <style>
        .login-container {max-width: 420px; margin: 0 auto; padding-top: 2rem;}
        .login-title {text-align: center; font-size: 28px; font-weight: 700;
                      color: #0d6efd; margin-bottom: 0;}
        .login-sub {text-align: center; color: #666; margin-bottom: 1.5rem;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>🏥 Sistema de Ausentismo Laboral</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-sub'>Seguridad y Salud en el Trabajo</div>", unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])

    with tab_login:
        with st.form("login_form"):
            usuario = st.text_input("👤 Usuario", value="dasb1512")
            clave = st.text_input("🔑 Contraseña", type="password", value="cocolizo76")
            submit = st.form_submit_button("Ingresar", use_container_width=True, type="primary")
            
            if submit:
                ok, msg, user = login(usuario.strip(), clave)
                if ok:
                    set_user(user)
                    st.success(f"Bienvenido, {user['nombre']}!")
                    st.rerun()
                else:
                    st.error(msg)

    with tab_register:
        render_register()

    st.markdown("</div>", unsafe_allow_html=True)
