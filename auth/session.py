"""Manejo de sesión con st.session_state."""
import streamlit as st


def init_session():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False


def set_user(user_row):
    st.session_state.user = user_row
    st.session_state.logged_in = True


def logout():
    st.session_state.user = None
    st.session_state.logged_in = False


def current_user():
    return st.session_state.get("user")


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def is_admin() -> bool:
    u = current_user()
    return bool(u and u.get("perfil") == "administrador")
