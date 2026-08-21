"""Carga de datos desde archivos Excel hacia Supabase."""
import pandas as pd
from io import BytesIO
from database.supabase_client import get_supabase

def _buscar_hoa(file, target_name: str) -> str | None:
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
    file.seek(0)
    df_raw = pd.read_excel(file, sheet_name=hoja, header=None, nrows=10)
    header_row_idx = None
    for i in range(len(df_raw)):
        row_values = df_raw.iloc[i].astype(str).str.strip().str.upper().tolist()
        if columna_clave.upper() in row_values:
            header_row_idx = i
            break
    if header_row_idx is None:
        return None, f"❌ No se encontró la columna '{columna_clave}' en las primeras 10 filas de la hoja '{hoja}'."
        
    file.seek(0)
    df = pd.read_excel(file, sheet_name=hoja, header=header_row_idx)
    df = df.dropna(how="all")
    df.columns = df.columns.astype(str).str.strip()
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df, None

def _limpiar_identificacion(val):
    """Convierte la identificación a texto sin decimales (.0) ni espacios."""
    val_str = str(val).strip()
    try:
        # Si es un número flotante como 1045690958.0, lo convierte a entero
        return str(int(float(val_str)))
    except:
        if val_str.lower() == "nan" or not val_str:
            return ""
        return val_str

def cargar_excel_ausentismo(file):
    hoja = _buscar_hoa(file, "AUSENTISMO")
    if not hoja: return 0, "❌ No se encontró la hoja 'AUSENTISMO'."
    df, err = _leer_excel_automatico(file, hoja, "IDENTIFICACION")
    if err: return 0, err

    sb = get_supabase()
    insertados = 0
    actualizados = 0
    errores = 0
    error_detalle = ""
    
    for _, r in df.iterrows():
        cedula = _limpiar_identificacion(r.get("IDENTIFICACION", ""))
        if not cedula: continue
        try:
            dias_val = r.get("DIAS PERDIDOS", 0)
            try:
                dias_perdidos = int(float(dias_val)) if str(dias_val).strip() != "" else 0
            except:
                dias_perdidos = 0

            fecha_ini = str(r.get("FECHA INICIAL", "")).strip()
            mes = str(r.get("MES", "")).strip()
            
            # Evitar duplicados: buscar por cedula, fecha_inicial y mes
            existing = sb.table("ausentismo").select("id").eq("cedula", cedula).eq("fecha_inicial", fecha_ini).eq("mes", mes).execute()
            
            data = {
                "cedula": cedula,
                "apellidos_nombres": str(r.get("APELLIDOS Y NOMBRES", "")).strip(),
                "cargo": str(r.get("CARGO", "")).strip(),
                "proceso": str(r.get("PROCESO", "")).strip(),
                "fecha_ingreso": str(r.get("FECHA DE INGRESO", "")).strip(),
                "salario": str(r.get("SALARIO", "")).strip(),
                "asunto": str(r.get("ASUNTO", "")).strip(),
                "tipo_incapacidad": str(r.get("TIPO DE INCAPACIDAD", "")).strip(),
                "fecha_inicial": fecha_ini,
                "fecha_final": str(r.get("FECHA FINAL", "")).strip(),
                "genera_incapacidad": str(r.get("GENERO INCAPACIDAD", "")).strip(),
                "dias_perdidos": dias_perdidos,
                "mes": mes,
                "costo_incapacidad": str(r.get("COSTO INCAPACIDAD", "")).strip(),
                "codigo_cie10": str(r.get("CODIGO CIE 10", "")).strip(),
                "diagnostico": str(r.get("DIAGNÓSTICO", "")).strip(),
                "dia_semana": str(r.get("DIA", "")).strip(),
            }
            
            if existing.data:
                sb.table("ausentismo").update(data).eq("id", existing.data[0]["id"]).execute()
                actualizados += 1
            else:
                sb.table("ausentismo").insert(data).execute()
                insertados += 1
        except Exception as e:
            if errores == 0: error_detalle = str(e)
            errores += 1
            
    msg = f"✅ {insertados} ausentismos nuevos. 🔄 {actualizados} actualizados."
    if errores > 0: msg += f" ⚠️ {errores} filas con error. Detalle: {error_detalle}"
    return insertados + actualizados, msg


def cargar_excel_base_datos(file):
    hoja = _buscar_hoa(file, "BASE DATOS")
    if not hoja: return 0, "❌ No se encontró la hoja 'BASE DATOS'."
    df, err = _leer_excel_automatico(file, hoja, "IDENTIFICACION")
    if err: return 0, err

    sb = get_supabase()
    insertados = 0
    actualizados = 0
    errores = 0
    error_detalle = ""
    
    for _, r in df.iterrows():
        ident = _limpiar_identificacion(r.get("IDENTIFICACION", ""))
        if not ident: continue
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
            "correo_personal": str(r.get("CORREO, PERSONAL", r.get("CORREO PERSONAL", ""))).strip(),
            "tel_familiar": str(r.get("TEL. FAMILIAR", "")).strip(),
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
            if errores == 0: error_detalle = str(e)
            errores += 1

    msg = f"✅ {insertados} trabajadores nuevos. 🔄 {actualizados} actualizados."
    if errores > 0: msg += f" ⚠️ {errores} filas con error. Detalle: {error_detalle}"
    return insertados + actualizados, msg


def cargar_excel_permisos(file):
    hoja = _buscar_hoa(file, "FORMATO")
    if not hoja: return 0, "❌ No se encontró la hoja 'FORMATO'."
    df, err = _leer_excel_automatico(file, hoja, "IDENTIFICACION")
    if err: return 0, err

    sb = get_supabase()
    insertados = 0
    actualizados = 0
    errores = 0
    error_detalle = ""
    
    for _, r in df.iterrows():
        cedula = _limpiar_identificacion(r.get("IDENTIFICACION", ""))
        if not cedula: continue
        try:
            fecha_ini = str(r.get("FECHA INICIAL", "")).strip()
            mes = str(r.get("MES", "")).strip()
            
            existing = sb.table("permisos_laborales").select("id").eq("cedula", cedula).eq("fecha_inicial", fecha_ini).eq("mes", mes).execute()
            
            data = {
                "cedula": cedula,
                "apellidos_nombres": str(r.get("APELLIDOS Y NOMBRES", "")).strip(),
                "cargo": str(r.get("CARGO", "")).strip(),
                "area": str(r.get("AREA", "")).strip(),
                "fecha_ingreso": str(r.get("FECHA DE INGRESO", "")).strip(),
                "asunto": str(r.get("ASUNTO", "")).strip(),
                "tipo_permiso": str(r.get("TIPO DE PERMISO", "")).strip(),
                "fecha_inicial": fecha_ini,
                "fecha_final": str(r.get("FECHA FINAL", "")).strip(),
                "hora_inicio": str(r.get("HORA INICIO", "")).strip(),
                "hora_final": str(r.get("HORA FINAL", "")).strip(),
                "descanso_almuerzo": str(r.get("DESCANSO/ HORA ALMUERZO", "")).strip(),
                "horas": str(r.get("HORAS", "")).strip(),
                "mes": mes,
            }
            
            if existing.data:
                sb.table("permisos_laborales").update(data).eq("id", existing.data[0]["id"]).execute()
                actualizados += 1
            else:
                sb.table("permisos_laborales").insert(data).execute()
                insertados += 1
        except Exception as e:
            if errores == 0: error_detalle = str(e)
            errores += 1
            
    msg = f"✅ {insertados} permisos nuevos. 🔄 {actualizados} actualizados."
    if errores > 0: msg += f" ⚠️ {errores} filas con error. Detalle: {error_detalle}"
    return insertados + actualizados, msg


def cargar_excel_emo(file):
    """Carga la hoja FORMATO de EMO y actualiza el estado en la tabla 'trabajadores'."""
    hoja = _buscar_hoa(file, "FORMATO")
    if not hoja: return 0, "❌ No se encontró la hoja 'FORMATO' en el archivo EMO."
    
    df, err = _leer_excel_automatico(file, hoja, "IDENTIFICACION")
    if err: return 0, err

    sb = get_supabase()
    actualizados = 0
    no_encontrados = 0
    errores = 0
    error_detalle = ""
    
    for _, r in df.iterrows():
        ident = _limpiar_identificacion(r.get("IDENTIFICACION", ""))
        if not ident: continue
            
        estado_excel = str(r.get("ESTADO DEL EMO", "")).strip()
        cumplimiento = str(r.get("CUMPLIMIENTO", "")).strip().upper()
        tipo_emo = str(r.get("TIPO DE EMO", "")).strip()
        
        # Si está en blanco, significa que no se ha realizado
        if not estado_excel or estado_excel.lower() == "nan":
            if "NO" in cumplimiento or "N/A" in cumplimiento or "NO APLICA" in cumplimiento:
                estado_calculado = "No Aplica"
            else:
                estado_calculado = "Pendiente"
        else:
            estado_calculado = "Realizado"

        try:
            # Actualizamos directamente en la tabla trabajadores
            existing = sb.table("trabajadores").select("id").eq("identificacion", ident).execute()
            if existing.data:
                sb.table("trabajadores").update({
                    "emo_periodico": estado_calculado,
                    "tipo_emo": tipo_emo
                }).eq("identificacion", ident).execute()
                actualizados += 1
            else:
                no_encontrados += 1
        except Exception as e:
            if errores == 0: error_detalle = str(e)
            errores += 1

    msg = f"✅ {actualizados} trabajadores actualizados con estado EMO Periódico."
    if no_encontrados > 0: msg += f" ⚠️ {no_encontrados} trabajadores no estaban en la BD."
    if errores > 0: msg += f" ❌ {errores} errores. Detalle: {error_detalle}"
    return actualizados, msg
