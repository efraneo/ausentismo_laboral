"""Asistente de IA para análisis de SST usando OpenAI."""
import streamlit as st
import pandas as pd
from openai import OpenAI
from config import OPENAI_API_KEY

def render_ai_assistant(df_aus: pd.DataFrame, df_tra: pd.DataFrame):
    st.markdown("## 🤖 Asistente Inteligente de SST (IA)")
    
    if not OPENAI_API_KEY:
        st.warning("⚠️ La API Key de OpenAI no está configurada en secrets.toml")
        return

    if df_aus.empty:
        st.info("No hay datos de ausentismo para analizar.")
        return

    st.markdown("Pregunta al asistente sobre los datos o genera un análisis estratégico:")
    
    col1, col2 = st.columns([3, 1])
    pregunta = col1.text_input("🔍 Tu pregunta", "Genera un resumen ejecutivo de la situación de ausentismo e indica qué proceso requiere más atención.")
    analizar = col2.button("Analizar con IA", use_container_width=True)

    if analizar:
        with st.spinner("🧠 La IA está analizando los datos..."):
            try:
                client = OpenAI(api_key=OPENAI_API_KEY)
                
                # Preparar resumen rápido de datos
                resumen_datos = f"""
                - Total casos ausentismo: {len(df_aus)}
                - Total días perdidos: {df_aus['dias_perdidos'].sum() if 'dias_perdidos' in df_aus else 0}
                - Por proceso: {df_aus['proceso'].value_counts().head(5).to_dict() if 'proceso' in df_aus else 'N/A'}
                - Por tipo: {df_aus['asunto'].value_counts().head(5).to_dict() if 'asunto' in df_aus else 'N/A'}
                - Top diagnósticos: {df_aus['diagnostico'].value_counts().head(5).to_dict() if 'diagnostico' in df_aus else 'N/A'}
                - Total trabajadores: {len(df_tra)}
                - Vinculados: {len(df_tra[df_tra['estado']=='Vinculado']) if 'estado' in df_tra else 0}
                """
                
                prompt_sistema = """
                Eres un experto en Seguridad y Salud en el Trabajo (SST) en Colombia. 
                Analiza los siguientes datos de ausentismo laboral y responde la pregunta del usuario 
                de forma profesional, clara y con viñetas. Da recomendaciones de mejora.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": f"Datos:\n{resumen_datos}\n\nPregunta: {pregunta}"}
                    ],
                    temperature=0.5
                )
                
                st.markdown("### 📝 Respuesta del Asistente")
                st.markdown(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"Error al conectar con OpenAI: {e}")
