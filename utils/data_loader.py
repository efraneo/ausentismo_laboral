"""Carga de datos desde archivos Excel hacia Supabase."""
import pandas as pd
from io import BytesIO
from database.supabase_client import get_supabase

def _buscar_hoa(file, target_name: str) -> str | None:
    """Busca el nombre de la hoja sin importar mayúsculas/minúsculas ni espacios."""
    try:
        file.seek(0)
        if hasattr(file, 'read'):
            content = file.read()
            xls = pd.ExcelFile(BytesIO(content))
        else:
            xls = pd.ExcelFile(file)
            
        target_upper = target_name.strip().upper()
        for sheet in xls.sheet_names:
            if sheet.strip().upper() == target_upper:
                return sheet
        return None
    except Exception:
        return None

def _leer_excel_automatico(file, hoja: str, columna_clave: str):
    """Lee el Excel escaneando las primeras 10 filas para encontrar el encabezado correcto."""
    file.seek(0)
    # 1. Leer las primeras 10 filas sin encabezados para buscar la fila clave
    df_raw = pd.read_excel(file, sheet_name=hoja, header=None, nrows=10)
    
    header_row_idx = None
    for i in range(len(df_raw)):
        row_values = df_raw.iloc[i].astype(str).str.strip().str.upper().tolist()
        if columna_clave.upper() in row_values:
            header_row_idx = i
            break
            
    if header_row_idx is None:
        return None, f"❌ No se encontró la columna '{columna_clave}' en las primeras 10 filas de la hoja '{hoja}'."
        
    # 2. Leer el Excel usando la fila correcta como encabezado
    file.seek(0)
    df = pd.read_excel(file, sheet_name=hoja, header=header_row_idx)
    df = df.dropna(how="all")
    # Limpiar nombres de columnas
    df.columns = df.columns.astype(str).str.strip()
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    
    return df, None


def cargar_excel_ausentismo(file):
    """Carga la hoja AUSENTISMO del Excel a Supabase."""
    hoja = _buscar_hoa(file, "AUSENTISMO")
    if not hoja:
        return 0, "❌ No se encontró la hoja 'AUSENTISMO'."
    
    # Buscamos la columna IDENTIFICACION
    df, err = _leer_excel_automatico(file, hoja, "IDENTIFICACION")
    if err:
        return 0, err

    sb = get_supabase()
    insertados = 0
    errores = 0
    error_detalle = ""
    
    for _, r in df.iterrows():
        cedula = str(r.get("IDENTIFICACION", "")).strip()
        if not cedula or cedula == "nan":
            continue
        try:
            dias_val = r.get("DIAS PERDIDOS", 0)
            try:
                dias_perdidos = int(float(dias_val)) if str(dias_val).strip() != "" else 0
            except:
                dias_perdidos = 0

            sb.table("ausentismo").insert({
                "cedula": cedula, # A Supabase se le envía a la columna 'cedula'
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
                "dias_perdidos": dias_perdidos,
                "mes": str(r.get("MES", "")).strip(),
                "costo_incapacidad": str(r.get("COSTO INCAPACIDAD", "")).strip(),
                "codigo_cie10": str(r.get("CODIGO CIE 10", "")).strip(),
                "diagnostico": str(r.get("DIAGNÓSTICO", "")).strip(),
                "dia_semana": str(r.get("DIA", "")).strip(),
            }).execute()
            insertados += 1
        except Exception as e:
            if errores == 0: 
                error_detalle = str(e)
            errores += 1
            
    if insertados == 0 and errores == 0:
        return 0, "⚠️ El archivo se leyó, pero no hay filas con IDENTIFICACION válida."
        
    msg = f"✅ {insertados} registros de ausentismo cargados."
    if errores > 0:
        msg += f" ⚠️ {errores} filas con error. Detalle del 1er error: {error_detalle}"
    return insertados, msg


def cargar_excel_base_datos(file):
    """Carga la hoja BASE DATOS (trabajadores) a Supabase."""
    hoja = _buscar_hoa(file, "BASE DATOS")
    if not hoja:
        return 0, "❌ No se encontró la hoja 'BASE DATOS'."
    
    df, err = _leer_excel_automatico(file, hoja, "IDENTIFICACION")
    if err:
        return 0, err

    sb = get_supabase()
    insertados = 0
    actualizados = 0
    errores = 0
    error_detalle = ""
    
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
            "hipertension_arterial": str(r.get("HIPERTENSION ARTERIAL", "NO")).strip().upper(),
            "obesidad": str(r.get("OBESIDAD", "NO")).strip().upper(),
            "diabetes": str(r.get("DIABETES", "NO")).strip().upper(),
            "cardiopatia": str(r.get("CARDIOPATIA", "NO")).strip().upper(),
            "hipotiroidismo": str(r.get("HIPOTIROIDISMO", "NO")).strip().upper(),
            "dislipidemia": str(r.get("DISLIPIDEMIA", "NO")).strip().upper(),
            "enfermedad_renal": str(r.get("ENFERMEDAD RENAL", "NO")).strip().upper(),
            "fumador": str(r.get("FUMADOR", "NO")).strip().upper(),
            "enfermedad_pulmonar": str(r.get("ENFERMEDAD PULMONAR", "NO")).strip().upper(),
            "estado": "Vinculado",
        }
        try:
            existing = sb.table("trabajadores").select("id, estado, emo_ingreso, emo_periodico, emo_retiro").eq("identificacion", ident).execute()
            if existing.data:
                estado_actual = existing.data[0].get("estado", "Vinculado")
                data["estado"] = estado_actual
                data["emo_ingreso"] = existing.data[0].get("emo_ingreso", "Pendiente")
                data["emo_periodico"] = existing.data[0].get("emo_periodico", "Pendiente")
                data["emo_retiro"] = existing.data[0].get("emo_retiro", "Pendiente")
                sb.table("trabajadores").update(data).eq("identificacion", ident).execute()
                actualizados += 1
            else:
                data["emo_ingreso"] = "Pendiente"
                data["emo_periodico"] = "Pendiente"
                data["emo_retiro"] = "Pendiente"
                sb.table("trabajadores").insert(data).execute()
                insertados += 1
        except Exception as e:
            if errores == 0:
                error_detalle = str(e)
            errores += 1

    if insertados == 0 and actualizados == 0 and errores == 0:
        return 0, "⚠️ El archivo se leyó, pero no hay filas con IDENTIFICACION válida."
        
    msg = f"✅ {insertados} trabajadores nuevos cargados."
    if actualizados > 0:
        msg += f" 🔄 {actualizados} trabajadores actualizados."
    if errores > 0:
        msg += f" ⚠️ {errores} filas con error. Detalle: {error_detalle}"
    return insertados + actualizados, msg


def cargar_excel_permisos(file):
    """Carga la hoja FORMATO de permisos laborales a Supabase."""
    hoja = _buscar_hoa(file, "FORMATO")
    if not hoja:
        return 0, "❌ No se encontró la hoja 'FORMATO'."
    
    # Buscamos la columna IDENTIFICACION
    df, err = _leer_excel_automatico(file, hoja, "IDENTIFICACION")
    if err:
        return 0, err

    sb = get_supabase()
    insertados = 0
    errores = 0
    error_detalle = ""
    
    for _, r in df.iterrows():
        cedula = str(r.get("IDENTIFICACION", "")).strip()
        if not cedula or cedula == "nan":
            continue
        try:
            sb.table("permisos_laborales").insert({
                "cedula": cedula, # A Supabase se le envía a la columna 'cedula'
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
            if errores == 0:
                error_detalle = str(e)
            errores += 1
            
    if insertados == 0 and errores == 0:
        return 0, "⚠️ El archivo se leyó, pero no hay filas con IDENTIFICACION válida."
        
    msg = f"✅ {insertados} permisos laborales cargados."
    if errores > 0:
        msg += f" ⚠️ {errores} filas con error. Detalle: {error_detalle}"
    return insertados, msg

def cargar_excel_emo(file):
    """Carga la hoja FORMATO de EMO a Supabase, cruzando estado, cumplimiento y tipo de EMO."""
    hoja = _buscar_hoa(file, "FORMATO")
    if not hoja:
        return 0, "❌ No se encontró la hoja 'FORMATO' en el archivo EMO."
    
    df, err = _leer_excel_automatico(file, hoja, "IDENTIFICACION")
    if err:
        return 0, err

    sb = get_supabase()
    insertados = 0
    actualizados = 0
    errores = 0
    error_detalle = ""
    
    for _, r in df.iterrows():
        ident = str(r.get("IDENTIFICACION", "")).strip()
        if not ident or ident == "nan":
            continue
            
        estado_excel = str(r.get("ESTADO DEL EMO", "")).strip()
        cumplimiento = str(r.get("CUMPLIMIENTO", "")).strip().upper()
        
        if estado_excel and estado_excel.lower() != "nan":
            estado_calculado = "Realizado"
        else:
            if "NO" in cumplimiento or "N/A" in cumplimiento or "NO APLICA" in cumplimiento:
                estado_calculado = "No Aplica"
            else:
                estado_calculado = "Pendiente"

        data = {
            "identificacion": ident,
            "apellidos_nombres": str(r.get("APELLIDOS Y NOMBRES", "")).strip(),
            "cargo": str(r.get("CARGO", "")).strip(),
            "area": str(r.get("AREA", "")).strip(),
            "nivel_escolaridad": str(r.get("NIVEL DE ESCOLARIDAD", "")).strip(),
            "fecha_ingreso": str(r.get("F. INICIO", "")).strip(),
            "eps": str(r.get("EPS", "")).strip(),
            "afp": str(r.get("AFP", "")).strip(),
            "sexo": str(r.get("SEXO", "")).strip(),
            "edad": str(r.get("EDAD", "")).strip(),
            "fecha_nacimiento": str(r.get("F. NACIMIENTO", "")).strip(),
            "direccion": str(r.get("DIRECCION", "")).strip(),
            "contacto": str(r.get("CONTACTO", "")).strip(),
            "correo_personal": str(r.get("CORREO, PERSONAL", r.get("CORREO PERSONAL", ""))).strip(),
            "tel_familiar": str(r.get("TEL. FAMILIAR", "")).strip(),
            "estado_emo_excel": estado_excel,
            "cumplimiento": str(r.get("CUMPLIMIENTO", "")).strip(),
            "estado_calculado": estado_calculado,
            "tipo_emo": str(r.get("TIPO DE EMO", "")).strip() # <-- NUEVO CAMPO LEÍDO DEL EXCEL
        }
        
        try:
            existing = sb.table("registro_emo").select("id").eq("identificacion", ident).execute()
            if existing.data:
                sb.table("registro_emo").update(data).eq("identificacion", ident).execute()
                actualizados += 1
            else:
                sb.table("registro_emo").insert(data).execute()
                insertados += 1
        except Exception as e:
            if errores == 0:
                error_detalle = str(e)
            errores += 1

    if insertados == 0 and actualizados == 0 and errores == 0:
        return 0, "⚠️ El archivo se leyó, pero no hay filas con IDENTIFICACION válida."
        
    msg = f"✅ {insertados} registros EMO nuevos cargados."
    if actualizados > 0:
        msg += f" 🔄 {actualizados} registros actualizados."
    if errores > 0:
        msg += f" ⚠️ {errores} filas con error. Detalle: {error_detalle}"
    return insertados + actualizados, msg
