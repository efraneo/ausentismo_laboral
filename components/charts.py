"""Generadores de gráficos con Plotly."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def chart_dias_por_mes(df: pd.DataFrame):
    if df.empty or "mes" not in df.columns:
        return go.Figure()
    agg = df.groupby("mes")["dias_perdidos"].sum().reindex(
        ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO",
         "AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"]).fillna(0).reset_index()
    fig = px.bar(agg, x="mes", y="dias_perdidos", color="dias_perdidos",
                 color_continuous_scale="Viridis", title="📈 Días Perdidos por Mes")
    fig.update_layout(xaxis_title="Mes", yaxis_title="Días perdidos")
    return fig


def chart_ausentismo_por_tipo(df: pd.DataFrame):
    if df.empty or "asunto" not in df.columns:
        return go.Figure()
    agg = df.groupby("asunto")["dias_perdidos"].sum().reset_index()
    fig = px.pie(agg, names="asunto", values="dias_perdidos",
                 title="🩺 Distribución por Tipo de Ausentismo",
                 hole=0.4)
    return fig


def chart_ausentismo_por_proceso(df: pd.DataFrame):
    if df.empty or "proceso" not in df.columns:
        return go.Figure()
    agg = df.groupby("proceso")["dias_perdidos"].sum().reset_index().sort_values("dias_perdidos", ascending=False)
    fig = px.bar(agg, x="dias_perdidos", y="proceso", orientation="h",
                 color="dias_perdidos", color_continuous_scale="Inferno",
                 title="🏥 Días Perdidos por Proceso")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def chart_top_diagnosticos(df: pd.DataFrame, top=10):
    if df.empty or "diagnostico" not in df.columns:
        return go.Figure()
    agg = df.groupby("diagnostico")["dias_perdidos"].sum().reset_index()
    agg = agg.sort_values("dias_perdidos", ascending=False).head(top)
    fig = px.bar(agg, x="dias_perdidos", y="diagnostico", orientation="h",
                 color="dias_perdidos", color_continuous_scale="Tealgrn",
                 title=f"🔬 Top {top} Diagnósticos (CIE-10)")
    return fig


def chart_accidentes_por_dia_semana(df: pd.DataFrame):
    if df.empty or "dia_semana" not in df.columns:
        return go.Figure()
    agg = df.groupby("dia_semana").size().reset_index(name="casos")
    orden = ["LUNES","MARTES","MIÉRCOLES","JUEVES","VIERNES","SÁBADO","DOMINGO"]
    agg["dia_semana"] = pd.Categorical(agg["dia_semana"], categories=orden, ordered=True)
    agg = agg.sort_values("dia_semana")
    fig = px.bar(agg, x="dia_semana", y="casos", color="casos",
                 color_continuous_scale="Sunset", title="📅 Accidentes por Día de la Semana")
    return fig


def chart_permisos_por_mes(df: pd.DataFrame):
    if df.empty or "mes" not in df.columns:
        return go.Figure()
    agg = df.groupby("mes").size().reset_index(name="cantidad")
    fig = px.line(agg, x="mes", y="cantidad", markers=True,
                  title="📋 Permisos Laborales por Mes")
    return fig


def chart_permisos_por_tipo(df: pd.DataFrame):
    if df.empty or "tipo_permiso" not in df.columns:
        return go.Figure()
    agg = df.groupby("tipo_permiso").size().reset_index(name="cantidad")
    fig = px.pie(agg, names="tipo_permiso", values="cantidad",
                 title="⏰ Distribución de Permisos por Tipo", hole=0.4)
    return fig

def chart_top_ausentismo_trabajadores(df: pd.DataFrame):
    if df.empty or "apellidos_nombres" not in df.columns or "dias_perdidos" not in df.columns:
        return go.Figure()
    agg = df.groupby("apellidos_nombres")["dias_perdidos"].sum().reset_index()
    agg = agg.sort_values("dias_perdidos", ascending=False).head(10)
    fig = px.bar(agg, x="dias_perdidos", y="apellidos_nombres", orientation="h",
                 color="dias_perdidos", color_continuous_scale="Reds",
                 title="🏆 Top 10 Trabajadores con más Días de Ausentismo",
                 labels={"apellidos_nombres": "Trabajador", "dias_perdidos": "Días Perdidos"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig

def chart_top_permisos_trabajadores(df: pd.DataFrame):
    if df.empty or "apellidos_nombres" not in df.columns:
        return go.Figure()
    # Convertir horas a numérico por si viene como texto
    df["horas_num"] = pd.to_numeric(df.get("horas", 0), errors='coerce').fillna(0)
    agg = df.groupby("apellidos_nombres")["horas_num"].sum().reset_index()
    agg = agg.sort_values("horas_num", ascending=False).head(10)
    fig = px.bar(agg, x="horas_num", y="apellidos_nombres", orientation="h",
                 color="horas_num", color_continuous_scale="Blues",
                 title="🏆 Top 10 Trabajadores con más Horas de Permiso",
                 labels={"apellidos_nombres": "Trabajador", "horas_num": "Horas de Permiso"})
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig
