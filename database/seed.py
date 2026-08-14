"""Crea o actualiza el usuario administrador por defecto."""
import bcrypt
from datetime import datetime, timezone
from database.supabase_client import get_supabase
from config import ADMIN_DEFAULT

def ensure_admin_user():
    sb = get_supabase()
    try:
        clave_hash = bcrypt.hashpw(ADMIN_DEFAULT["clave"].encode(), bcrypt.gensalt()).decode()
        
        # Verificar si existe
        resp = sb.table("usuarios").select("id").eq("usuario", ADMIN_DEFAULT["usuario"]).execute()
        
        if resp.data:
            # Si existe, actualizar su clave y estado por si acaso
            sb.table("usuarios").update({
                "clave_hash": clave_hash,
                "estado": "aprobado",
                "perfil": "administrador",
                "correo": ADMIN_DEFAULT.get("correo", "")
            }).eq("usuario", ADMIN_DEFAULT["usuario"]).execute()
            print("✅ Administrador actualizado correctamente.")
        else:
            # Si no existe, crearlo
            sb.table("usuarios").insert({
                "usuario": ADMIN_DEFAULT["usuario"],
                "nombre": ADMIN_DEFAULT["nombre"],
                "correo": ADMIN_DEFAULT.get("correo", ""),
                "clave_hash": clave_hash,
                "identificacion": ADMIN_DEFAULT["identificacion"],
                "cargo": ADMIN_DEFAULT["cargo"],
                "fecha_nacimiento": ADMIN_DEFAULT["fecha_nacimiento"],
                "perfil": ADMIN_DEFAULT["perfil"],
                "estado": "aprobado",
                "caducidad": ADMIN_DEFAULT["caducidad"],
                "ingresos_sistema": 0,
                "ultimo_ingreso": datetime.now(timezone.utc).isoformat(),
            }).execute()
            print("✅ Administrador por defecto creado.")
            
    except Exception as e:
        print(f"⚠️  No se pudo crear/actualizar admin: {e}")

if __name__ == "__main__":
    ensure_admin_user()
