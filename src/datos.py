"""Carga y transformación de los datos de Superstore."""
from pathlib import Path

import pandas as pd
import streamlit as st

# Ruta relativa a la raíz del repositorio (este archivo vive en src/)
RUTA_DATOS = Path(__file__).resolve().parent.parent / "data" / "Sample - Superstore.csv"
RUTA_VISIBLE = "data/Sample - Superstore.csv"

# Etiqueta en español -> columna del conjunto de datos
DIMENSIONES = {
    "Descuento": "Descuento",
    "Subcategoría": "Sub-Category",
    "Categoría": "Category",
    "Región": "Region",
    "Segmento": "Segment",
    "Modo de envío": "Ship Mode",
}


@st.cache_data(show_spinner="Cargando datos…")
def cargar_datos() -> pd.DataFrame:
    """Lee el CSV igual que el notebook y agrega las columnas derivadas."""
    df = pd.read_csv(RUTA_DATOS, encoding="latin-1", dtype={"Postal Code": str})
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%m/%d/%Y")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%m/%d/%Y")
    df["Postal Code"] = df["Postal Code"].str.zfill(5)
    df["Pérdida"] = (df["Profit"] < 0).astype(int)
    df["Año"] = df["Order Date"].dt.year
    # Nivel de descuento como categoría ordenada ("0 %", "10 %", …)
    niveles = sorted(df["Discount"].unique())
    etiquetas = [f"{round(n * 100)} %" for n in niveles]
    df["Descuento"] = pd.Categorical(
        df["Discount"].map(dict(zip(niveles, etiquetas))), categories=etiquetas, ordered=True
    )
    return df


def obtener_datos() -> pd.DataFrame:
    """Devuelve los datos o detiene la app con un mensaje claro si falta el CSV."""
    try:
        return cargar_datos()
    except FileNotFoundError:
        st.error(
            f"No se encontró el archivo de datos **`{RUTA_VISIBLE}`**.\n\n"
            "Descargá *Sample - Superstore.csv* desde "
            "[Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) "
            "y guardalo en la carpeta `data/` del proyecto."
        )
        st.stop()


@st.cache_data
def tasa_por(df: pd.DataFrame, columna: str) -> pd.DataFrame:
    """Líneas, pérdidas y tasa de pérdida (%) por cada valor de `columna`."""
    tabla = (
        df.groupby(columna, observed=True)["Pérdida"]
        .agg(lineas="size", perdidas="sum")
        .reset_index()
    )
    tabla["tasa"] = tabla["perdidas"] / tabla["lineas"] * 100
    tabla[columna] = tabla[columna].astype(str)
    return tabla


@st.cache_data
def tasa_cruzada(df: pd.DataFrame, filas: str, columnas: str):
    """Matrices de tasa de pérdida (%) y de cantidad de líneas para dos dimensiones."""
    grupo = df.groupby([filas, columnas], observed=True)["Pérdida"]
    tasa = (grupo.mean() * 100).unstack(columnas)
    lineas = grupo.size().unstack(columnas)
    return tasa, lineas


@st.cache_data
def serie_mensual(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(pd.Grouper(key="Order Date", freq="MS"))[["Sales", "Profit"]]
        .sum()
        .reset_index()
    )
