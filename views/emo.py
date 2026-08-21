"""Página de gestión de EMO (solo administrador) con carga de archivos."""
import streamlit as st
import pandas as pd
from utils.helpers import fetch_trabajadores, update_emo
from auth.session import is_admin
from datetime import date
from database.supabase_client import get_supabase


def render_emo():
    st.markdown("## 🩺 Exámenes Médicos Ocupacionales (EMO)")
    if not is_admin():
        st.error("⛔ Solo el administrador puede gestionar EMO.")
        return

    df = fetch_trabajadores()
    if df.empty:
        st.warning("No hay trabajadores.")
        return

    sb = get_supabase()
    
    st.markdown("### 📋 Resumen General")
    c1, c2, c3 = st.columns(3)
    c1.metric("EMO Ingreso Pendientes",
              int((df["emo_ingreso"].astype(str).str.lower() == "pendiente").sum()) if "emo_ingreso" in df else 0)
    c2.metric("EMO Periódico Pendientes",
              int((df["emo_periodico"].astype(str).str.lower() == "pendiente").sum()) if "emo_periodico" in df else 0)
    c3.metric("EMO Retiro Pendientes",
              int((df["emo_retiro"].astype(str).str.lower() == "pendiente").sum()) if "emo_retiro" in df else 0)

    st.markdown("---")
    st.markdown("### 📝 Gestionar EMO y Adjuntar Concepto Médico (PDF)")

    df_sel = df.copy()
    df_sel["label"] = df_sel["apellidos_nombres"].astype(str) + " — CC: " + df_sel["identificacion"].astype(str)
    sel = st.selectbox("Selecciona el Trabajador", df_sel["label"].tolist())

    if sel:
        worker_row = df_sel[df_sel["label"] == sel].iloc[0]
        tid = worker_row["id"]
        ident = str(worker_row["identificacion"])
        
        col1, col2, col3 = st.columns(3)
        
        def render_emo_column(col, titulo, estado_actual, url_actual, campo_estado, campo_url):
            col.markdown(f"#### {titulo}")
            actual_str = str(estado_actual) if str(estado_actual) != "nan" else "Pendiente"
            
            op = col.radio("Estado:", ["Pendiente", "Realizado"], 
                           index=1 if "realizado" in actual_str.lower() else 0, 
                           key=f"op_{campo_estado}")
            
            fecha_val = None
            file_val = None
            
            if op == "Realizado":
                try:
                    fecha_default = pd.to_datetime(actual_str, dayfirst=True, errors="raise").date()
                except:
                    fecha_default = date.today()
                    
                fecha_val = col.date_input("Fecha EMO", value=fecha_default, key=f"date_{campo_estado}").strftime("%d/%m/%Y")
                
                # Mostrar si hay archivo o si falta
                if url_actual and str(url_actual) != "nan":
                    col.success(f"✅ [Ver Concepto Médico]({url_actual})", icon="📄")
                else:
                    col.warning("⚠️ Falta adjuntar PDF", icon="⚠️")
                
                file_val = col.file_uploader(f"Subir PDF", type=["pdf"], key=f"file_{campo_estado}")
            else:
                col.info("No requiere archivo (Pendiente).")
                    
            return op, fecha_val, file_val

        v_ingreso = render_emo_column(col1, "EMO de Ingreso", worker_row.get("emo_ingreso", "Pendiente"), worker_row.get("emo_ingreso_url"), "emo_ingreso", "emo_ingreso_url")
        v_periodico = render_emo_column(col2, "EMO Periódico", worker_row.get("emo_periodico", "Pendiente"), worker_row.get("emo_periodico_url"), "emo_periodico", "emo_periodico_url")
        v_retiro = render_emo_column(col3, "EMO de Retiro", worker_row.get("emo_retiro", "Pendiente"), worker_row.get("emo_retiro_url"), "emo_retiro", "emo_retiro_url")

        if st.button("💾 Guardar y Subir Archivos", use_container_width=True, type="primary"):
            updates = {}
            
            # Procesar Ingreso
            updates["emo_ingreso"] = v_ingreso[1] if v_ingreso[0] == "Realizado" else "Pendiente"
            if v_ingreso[0] == "Realizado" and v_ingreso[2] is not None:
                file_name = f"{ident}_ingreso.pdf"
                try:
                    sb.storage.from_("emo-archivos").upload(file_name, v_ingreso[2].getvalue(), file_options={"content-type": "application/pdf", "upsert": "true"})
                    updates["emo_ingreso_url"] = sb.storage.from_("emo-archivos").get_public_url(file_name)
                except Exception as e:
                    st.error(f"Error subiendo PDF Ingreso: {e}")
                    
            # Procesar Periódico
            updates["emo_periodico"] = v_periodico[1] if v_periodico[0] == "Realizado" else "Pendiente"
            if v_periodico[0] == "Realizado" and v_periodico[2] is not None:
                file_name = f"{ident}_periodico.pdf"
                try:
                    sb.storage.from_("emo-archivos").upload(file_name, v_periodico[2].getvalue(), file_options={"content-type": "application/pdf", "upsert": "true"})
                    updates["emo_periodico_url"] = sb.storage.from_("emo-archivos").get_public_url(file_name)
                except Exception as e:
                    st.error(f"Error subiendo PDF Periódico: {e}")
                    
            # Procesar Retiro
            updates["emo_retiro"] = v_retiro[1] if v_retiro[0] == "Realizado" else "Pendiente"
            if v_retiro[0] == "Realizado" and v_retiro[2] is not None:
                file_name = f"{ident}_retiro.pdf"
                try:
                    sb.storage.from_("emo-archivos").upload(file_name, v_retiro[2].getvalue(), file_options={"content-type": "application/pdf", "upsert": "true"})
                    updates["emo_retiro_url"] = sb.storage.from_("emo-archivos").get_public_url(file_name)
                except Exception as e:
                    st.error(f"Error subiendo PDF Retiro: {e}")

            try:
                sb.table("trabajadores").update(updates).eq("id", tid).execute()
                st.success("✅ EMO y conceptos médicos actualizados correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error guardando en BD: {e}")

    st.markdown("---")
    st.markdown("### 📄 Tabla General de EMO")
    show = ["identificacion","apellidos_nombres","cargo","area","estado",
            "emo_ingreso","emo_periodico","emo_retiro"]
    show = [c for c in show if c in df.columns]
    st.dataframe(df[show], use_container_width=True, height=500, hide_index=True)
