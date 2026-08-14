"""Carga de datos desde archivos Excel hacia Supabase."""
import pandas as pd
from database.supabase_client import get_supabase


def cargar_excel_ausentismo(ruta_excel: str):
    """Carga la hoja AUSENTISMO del Excel a Supabase."""
    df = pd.read_excel(ruta_excel, sheet_name="AUSENTISMO", header=4)
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    sb = get_supabase()
    insertados = 0
    for _, r in df.iterrows():
        cedula = str(r.get("CEDULA", "")).strip()
        if not cedula or cedula == "nan":
            continue
        try:
            sb.table("ausentismo").insert({
                "cedula": cedula,
                "apellidos_nombres": str(r.get("APELLIDOS Y NOMBRES", "")).strip(),
                "cargo": str(r.get("CARGO", "")).strip(),
                "proceso": str(r.get("PROCESO", "")).strip(),
                "fecha_ingreso": str(r.get("FECHA DE INGRESO", "")).strip(),
                "salario": str(r.get("SALARIO", "")).strip(),
                "asunto": str(r.get("ASUNTO", "")).strip(),
                "tipo_incapacidad": str(r.get("TIPO DE INCAPACIDAD", "")).strip(),
                "fecha_inicial": str(r.get("FECHA INICIAL", "")).strip(),
                "fecha_final": str(r.get("FECHA FINAL", "")).strip(),
                "genera_incapacidad": str(r.get("GENERO INCAPACIDAD", "")).strip(),
                "dias_perdidos": int(r.get("DIAS PERDIDOS", 0) or 0),
                "mes": str(r.get("MES", "")).strip(),
                "costo_incapacidad": str(r.get("COSTO INCAPACIDAD", "")).strip(),
                "codigo_cie10": str(r.get("CODIGO CIE 10", "")).strip(),
                "diagnostico": str(r.get("DIAGNÓSTICO", "")).strip(),
                "dia_semana": str(r.get("DIA", "")).strip(),
            }).execute()
            insertados += 1
        except Exception as e:
            print(f"Error fila ausentismo: {e}")
    return insertados


def cargar_excel_base_datos(ruta_excel: str):
    """Carga la hoja BASE DATOS (trabajadores) a Supabase."""
    df = pd.read_excel(ruta_excel, sheet_name="BASE DATOS", header=1)
    df = df.dropna(how="all")
    sb = get_supabase()
    insertados = 0
    for _, r in df.iterrows():
        ident = str(r.get("IDENTIFICACION", "")).strip()
        if not ident or ident == "nan":
            continue
        data = {
            "identificacion": ident,
            "apellidos_nombres": str(r.get("APELLIDOS Y NOMBRES", "")).strip(),
            "cargo": str(r.get("CARGO", "")).strip(),
            "area": str(r.get("AREA", "")).strip(),
            "nivel_escolaridad": str(r.get("NIVEL DE ESCOLARIDAD", "")).strip(),
            "salario": str(r.get("SALARIO", "")).strip(),
            "fecha_ingreso": str(r.get("F. INICIO", "")).strip(),
            "eps": str(r.get("EPS", "")).strip(),
            "afp": str(r.get("AFP", "")).strip(),
            "sexo": str(r.get("SEXO", "")).strip(),
            "edad": str(r.get("EDAD", "")).strip(),
            "fecha_nacimiento": str(r.get("F. NACIMIENTO", "")).strip(),
            "direccion": str(r.get("DIRECCION", "")).strip(),
            "contacto": str(r.get("CONTACTO", "")).strip(),
            "correo_personal": str(r.get("CORREO PERSONAL", "")).strip(),
            "tel_familiar": str(r.get("TEL. FAMILIAR", "")).strip(),
            "hipertension_arterial": str(r.get("HIPERTENSION ARTERIAL", "NO")).strip(),
            "obesidad": str(r.get("OBESIDAD", "NO")).strip(),
            "diabetes": str(r.get("DIABETES", "NO")).strip(),
            "cardiopatia": str(r.get("CARDIOPATIA", "NO")).strip(),
            "hipotiroidismo": str(r.get("HIPOTIROIDISMO", "NO")).strip(),
            "dislipidemia": str(r.get("DISLIPIDEMIA", "NO")).strip(),
            "enfermedad_renal": str(r.get("ENFERMEDAD RENAL", "NO")).strip(),
            "fumador": str(r.get("FUMADOR", "NO")).strip(),
            "enfermedad_pulmonar": str(r.get("ENFERMEDAD PULMONAR", "NO")).strip(),
            "estado": "Vinculado",
            "emo_ingreso": "Pendiente",
            "emo_periodico": "Pendiente",
            "emo_retiro": "Pendiente",
        }
        try:
            # upsert por identificacion
            existing = sb.table("trabajadores").select("id").eq("identificacion", ident).execute()
            if existing.data:
                sb.table("trabajadores").update(data).eq("identificacion", ident).execute()
            else:
                sb.table("trabajadores").insert(data).execute()
            insertados += 1
        except Exception as e:
            print(f"Error fila trabajador: {e}")
    return insertados


def cargar_excel_permisos(ruta_excel: str):
    """Carga la hoja Formato de permisos laborales a Supabase."""
    df = pd.read_excel(ruta_excel, sheet_name="Formato", header=1)
    df = df.dropna(how="all")
    sb = get_supabase()
    insertados = 0
    for _, r in df.iterrows():
        cedula = str(r.get("CEDULA", "")).strip()
        if not cedula or cedula == "nan":
            continue
        try:
            sb.table("permisos_laborales").insert({
                "cedula": cedula,
                "apellidos_nombres": str(r.get("APELLIDOS Y NOMBRES", "")).strip(),
                "cargo": str(r.get("CARGO", "")).strip(),
                "area": str(r.get("AREA", "")).strip(),
                "fecha_ingreso": str(r.get("FECHA DE INGRESO", "")).strip(),
                "asunto": str(r.get("ASUNTO", "")).strip(),
                "tipo_permiso": str(r.get("TIPO DE PERMISO", "")).strip(),
                "fecha_inicial": str(r.get("FECHA INICIAL", "")).strip(),
                "fecha_final": str(r.get("FECHA FINAL", "")).strip(),
                "hora_inicio": str(r.get("HORA INICIO", "")).strip(),
                "hora_final": str(r.get("HORA FINAL", "")).strip(),
                "descanso_almuerzo": str(r.get("DESCANSO/ HORA ALMUERZO", "")).strip(),
                "horas": str(r.get("HORAS", "")).strip(),
                "mes": str(r.get("MES", "")).strip(),
            }).execute()
            insertados += 1
        except Exception as e:
            print(f"Error fila permiso: {e}")
    return insertados
