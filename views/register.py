"""Página de registro con 2FA."""
import streamlit as st
from auth.authentication import registrar_usuario, verificar_2fa, reenviar_2fa


def render_register():
    st.markdown("### 📝 Registro de nuevo usuario")
    with st.form("register_form"):
        nombre = st.text_input("Nombre completo *")
        usuario = st.text_input("Usuario *")
        correo = st.text_input("Correo electrónico *")
        identificacion = st.text_input("Identificación")
        cargo = st.text_input("Cargo")
        clave = st.text_input("Contraseña *", type="password")
        clave2 = st.text_input("Confirmar contraseña *", type="password")
        submit = st.form_submit_button("Registrarme", use_container_width=True)

        if submit:
            if not all([nombre, usuario, correo, clave]):
                st.error("Completa los campos obligatorios (*)")
            elif clave != clave2:
                st.error("Las contraseñas no coinciden")
            else:
                ok, msg = registrar_usuario(
                    usuario.strip(), nombre.strip(), correo.strip(),
                    clave, identificacion.strip(), cargo.strip()
                )
                if ok:
                    st.success(msg)
                    st.session_state["pending_2fa_user"] = usuario.strip()
                    st.rerun()
                else:
                    st.error(msg)

    # Verificación 2FA
    if st.session_state.get("pending_2fa_user"):
        st.markdown("---")
        st.markdown("### 🔐 Verificación 2FA")
        st.info(f"Hemos enviado un código a tu correo. Ingrésalo para verificar.")
        with st.form("verify_2fa_form"):
            codigo = st.text_input("Código de 6 dígitos", max_chars=6)
            col1, col2 = st.columns([3, 1])
            verificar = col1.form_submit_button("Verificar", use_container_width=True, type="primary")
            reenviar = col2.form_submit_button("Reenviar")
            if verificar:
                ok, msg = verificar_2fa(st.session_state["pending_2fa_user"], codigo)
                if ok:
                    st.success(msg + " Ahora espera aprobación del administrador.")
                    st.session_state.pop("pending_2fa_user", None)
                    st.rerun()
                else:
                    st.error(msg)
            if reenviar:
                ok, msg = reenviar_2fa(st.session_state["pending_2fa_user"])
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
