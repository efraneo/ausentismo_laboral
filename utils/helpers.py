"""Funciones auxiliares."""
import pandas as pd
from database.supabase_client import get_supabase


def fetch_ausentismo():
    sb = get_supabase()
    r = sb.table("ausentismo").select("*").order("id", desc=True).execute()
    return pd.DataFrame(r.data)


def fetch_permisos():
    sb = get_supabase()
    r = sb.table("permisos_laborales").select("*").order("id", desc=True).execute()
    return pd.DataFrame(r.data)


def fetch_trabajadores(estado: str | None = None):
    sb = get_supabase()
    q = sb.table("trabajadores").select("*").order("apellidos_nombres")
    if estado:
        q = q.eq("estado", estado)
    r = q.execute()
    return pd.DataFrame(r.data)


def fetch_usuarios():
    sb = get_supabase()
    r = sb.table("usuarios").select("*").order("id", desc=True).execute()
    return pd.DataFrame(r.data)


def update_trabajador_estado(trabajador_id, estado):
    sb = get_supabase()
    sb.table("trabajadores").update({"estado": estado}).eq("id", trabajador_id).execute()


def update_emo(trabajador_id, campo, valor):
    """Actualiza un campo EMO (emo_ingreso, emo_periodico, emo_retiro)."""
    sb = get_supabase()
    sb.table("trabajadores").update({campo: valor}).eq("id", trabajador_id).execute()
