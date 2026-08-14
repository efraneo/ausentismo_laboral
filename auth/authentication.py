"""Lógica de autenticación: login, registro, 2FA."""
import secrets
from datetime import datetime, timedelta, timezone
import bcrypt
from database.supabase_client import get_supabase
from auth.email_service import enviar_codigo_2fa, notificar_admin_registro
from config import ADMIN_DEFAULT, TWO_FACTOR_EXPIRY_SECONDS

def _hash_password(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()

def _check_password(p: str, h: str) -> bool:
    try: return bcrypt.checkpw(p.encode(), h.encode())
    except: return False

def registrar_usuario(usuario, nombre, correo, clave, identificacion="", cargo=""):
    sb = get_supabase()
    if sb.table("usuarios").select("id").eq("usuario", usuario).execute().data:
        return False, "El usuario ya existe."
    if correo and sb.table("usuarios").select("id").eq("correo", correo).execute().data:
        return False, "El correo ya está registrado."

    codigo = f"{secrets.randbelow(900000) + 100000}"
    expira = (datetime.now(timezone.utc) + timedelta(seconds=TWO_FACTOR_EXPIRY_SECONDS)).isoformat()

    sb.table("usuarios").insert({
        "usuario": usuario, "nombre": nombre, "correo": correo,
        "clave_hash": _hash_password(clave), "identificacion": identificacion,
        "cargo": cargo, "perfil": "consulta", "estado": "pendiente",
        "caducidad": "Indefinido", "codigo_2fa": codigo, "codigo_2fa_expira": expira,
    }).execute()

    if correo: enviar_codigo_2fa(correo, nombre, codigo)
    
    # Notificar al Admin
    notificar_admin_registro(nombre, usuario, correo)
    
    return True, f"Registro exitoso. Se envió código 2FA a {correo}."

def verificar_2fa(usuario, codigo):
    sb = get_supabase()
    resp = sb.table("usuarios").select("codigo_2fa, codigo_2fa_expira").eq("usuario", usuario).execute()
    if not resp.data: return False, "Usuario no encontrado."
    row = resp.data[0]
    if not row.get("codigo_2fa"): return False, "No hay código pendiente."
    expira = row.get("codigo_2fa_expira")
    if expira and datetime.fromisoformat(expira.replace("Z", "+00:00")) < datetime.now(timezone.utc):
        return False, "El código expiró. Solicita uno nuevo."
    if str(row["codigo_2fa"]).strip() != str(codigo).strip():
        return False, "Código incorrecto."
    sb.table("usuarios").update({"codigo_2fa": None, "codigo_2fa_expira": None, "estado": "pendiente_aprobacion"}).eq("usuario", usuario).execute()
    return True, "Correo verificado. Un administrador aprobará tu cuenta."

def login(usuario, clave):
    sb = get_supabase()
    resp = sb.table("usuarios").select("*").eq("usuario", usuario).execute()
    if not resp.data: return False, "Usuario no encontrado.", None
    row = resp.data[0]
    if not _check_password(clave, row["clave_hash"]): return False, "Contraseña incorrecta.", None
    if row["estado"] != "aprobado": return False, f"Tu cuenta está: {row['estado']}. Contacta al administrador.", None
    
    sb.table("usuarios").update({
        "ingresos_sistema": (row.get("ingresos_sistema") or 0) + 1,
        "ultimo_ingreso": datetime.now(timezone.utc).isoformat(),
    }).eq("id", row["id"]).execute()
    return True, "Login exitoso", row

def aprobar_usuario(user_id):
    get_supabase().table("usuarios").update({"estado": "aprobado"}).eq("id", user_id).execute()
    return True

def rechazar_usuario(user_id):
    get_supabase().table("usuarios").update({"estado": "rechazado"}).eq("id", user_id).execute()
    return True

def reenviar_2fa(usuario):
    sb = get_supabase()
    resp = sb.table("usuarios").select("*").eq("usuario", usuario).execute()
    if not resp.data: return False, "Usuario no encontrado."
    row = resp.data[0]
    if row["estado"] != "pendiente": return False, "El usuario ya no está pendiente."
    codigo = f"{secrets.randbelow(900000) + 100000}"
    expira = (datetime.now(timezone.utc) + timedelta(seconds=TWO_FACTOR_EXPIRY_SECONDS)).isoformat()
    sb.table("usuarios").update({"codigo_2fa": codigo, "codigo_2fa_expira": expira}).eq("id", row["id"]).execute()
    if row.get("correo"): enviar_codigo_2fa(row["correo"], row["nombre"], codigo)
    return True, "Código reenviado."
