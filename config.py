"""Configuración central leyendo directamente desde st.secrets."""
import streamlit as st

def get_secret(key, default=None):
    """Lee un secret de Streamlit. Si está vacío o no existe, usa el default."""
    try:
        val = st.secrets[key]
        # Si el valor existe pero es un string vacío "", devolvemos el default
        return val if val != "" else default
    except Exception:
        return default

# Supabase
SUPABASE_URL = get_secret("SUPABASE_URL", "")
SUPABASE_KEY = get_secret("SUPABASE_KEY", "")

# Email SMTP
EMAIL_HOST = get_secret("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(get_secret("EMAIL_PORT", 587))
EMAIL_USER = get_secret("EMAIL_USER", "")
EMAIL_PASSWORD = get_secret("EMAIL_PASSWORD", "")
EMAIL_FROM_NAME = get_secret("EMAIL_FROM_NAME", "Ausentismo Laboral 2026 By EESC")
ADMIN_EMAIL = get_secret("ADMIN_EMAIL", "")

# 2FA
TWO_FACTOR_EXPIRY_SECONDS = int(get_secret("TWO_FACTOR_EXPIRY_SECONDS", 300))

# OpenAI
OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "")

# Administrador por defecto (Lee el secret, pero tiene la clave 'cocolizo76' como respaldo)
ADMIN_DEFAULT = {
    "usuario": "dasb1512",  # Fijo según tu solicitud
    "nombre": "Efrain Sarmiento Crespo",
    "clave": get_secret("ADMIN_PASSWORD", "cocolizo76"),  # Lee de secrets, respalda con cocolizo76
    "fecha_nacimiento": "19/09/2026",
    "perfil": "administrador",
    "cargo": "Jefe de SST",
    "identificacion": "8642239",
    "caducidad": "Indefinido",
    "correo": ADMIN_EMAIL
}

ESTADOS_TRABAJADOR = ["Vinculado", "Desvinculado"]
ESTADOS_EMO = ["Pendiente"]
PERFILES = ["administrador", "consulta"]
