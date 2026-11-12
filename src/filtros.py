"""Filtros globales de la barra lateral (afectan a las páginas 1 a 3)."""
import pandas as pd
import streamlit as st


def barra_filtros(df: pd.DataFrame, activos: bool) -> None:
    """Dibuja los filtros. Se dibujan siempre para conservar la selección entre páginas."""
    anios = (int(df["Año"].min()), int(df["Año"].max()))
    with st.sidebar:
        st.header("Filtros")
        if not activos:
            st.caption("Esta página usa el modelo entrenado; los filtros no aplican aquí.")
        st.multiselect("Categoría", sorted(df["Category"].unique()), key="f_categoria",
                       placeholder="Todas", disabled=not activos)
        st.multiselect("Región", sorted(df["Region"].unique()), key="f_region",
                       placeholder="Todas", disabled=not activos)
        st.multiselect("Segmento", sorted(df["Segment"].unique()), key="f_segmento",
                       placeholder="Todos", disabled=not activos)
        st.slider("Años", anios[0], anios[1], anios, key="f_anios", disabled=not activos)


def aplicar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra según la barra lateral. Una lista vacía significa «todos»."""
    estado = st.session_state
    mascara = pd.Series(True, index=df.index)
    for clave, columna in [("f_categoria", "Category"), ("f_region", "Region"), ("f_segmento", "Segment")]:
        if estado.get(clave):
            mascara &= df[columna].isin(estado[clave])
    if "f_anios" in estado:
        mascara &= df["Año"].between(*estado["f_anios"])
    filtrado = df[mascara]
    if filtrado.empty:
        st.warning("No hay líneas de pedido con esa combinación de filtros. Probá ampliar la selección.")
        st.stop()
    if len(filtrado) < len(df):
        st.caption(f"Filtros activos: {len(filtrado):,} de {len(df):,} líneas.".replace(",", "."))
    return filtrado
