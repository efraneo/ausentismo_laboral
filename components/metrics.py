"""Indicadores / KPIs del dashboard."""
import pandas as pd


def kpi_total_dias_perdidos(df: pd.DataFrame) -> int:
    if df.empty or "dias_perdidos" not in df.columns:
        return 0
    return int(df["dias_perdidos"].sum())


def kpi_total_casos(df: pd.DataFrame) -> int:
    return len(df)


def kpi_total_accidentes(df: pd.DataFrame) -> int:
    if df.empty or "asunto" not in df.columns:
        return 0
    return int((df["asunto"].str.upper() == "ACCIDENTE DE TRABAJO").sum())


def kpi_costo_total(df: pd.DataFrame) -> float:
    if df.empty or "costo_incapacidad" not in df.columns:
        return 0.0
    s = df["costo_incapacidad"].astype(str).str.replace(r"[^\d.]", "", regex=True)
    s = pd.to_numeric(s, errors="coerce").fillna(0)
    return float(s.sum())


def kpi_total_trabajadores() -> int:
    return 0  # se carga dinámicamente desde la página


def kpi_vinculados(df: pd.DataFrame) -> int:
    if df.empty or "estado" not in df.columns:
        return 0
    return int((df["estado"] == "Vinculado").sum())


def kpi_desvinculados(df: pd.DataFrame) -> int:
    if df.empty or "estado" not in df.columns:
        return 0
    return int((df["estado"] == "Desvinculado").sum())


def kpi_emo_pendientes(df: pd.DataFrame) -> int:
    if df.empty or "emo_periodico" not in df.columns:
        return 0
    # Contar solo los EMO Periódicos que estén estrictamente "Pendiente"
    return int((df["emo_periodico"].astype(str).str.lower() == "pendiente").sum())
