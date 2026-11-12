import streamlit as st

from src import graficos
from src.datos import DIMENSIONES, obtener_datos, tasa_cruzada, tasa_por
from src.filtros import aplicar_filtros

st.title("Explorar el riesgo")
st.caption("Tasa de pérdida: porcentaje de líneas de pedido con ganancia negativa.")

df = aplicar_filtros(obtener_datos())
tasa_global = df["Pérdida"].mean() * 100

control, cruce = st.columns(2)
dimension = control.selectbox("Dimensión", list(DIMENSIONES))
otras = [d for d in DIMENSIONES if d != dimension]
segunda = cruce.selectbox("Cruzar con (opcional)", ["Sin cruce"] + otras)

columna = DIMENSIONES[dimension]
tabla = tasa_por(df, columna)
es_descuento = dimension == "Descuento"
if not es_descuento:
    tabla = tabla.sort_values("tasa")
st.plotly_chart(graficos.barras_tasa(
    tabla, columna, tasa_global, f"Tasa de pérdida por {dimension.lower()}",
    horizontal=not es_descuento))

if segunda != "Sin cruce":
    # El descuento va siempre en el eje horizontal para leerlo de menor a mayor
    filas, columnas = (segunda, dimension) if es_descuento else (dimension, segunda)
    tasa, lineas = tasa_cruzada(df, DIMENSIONES[filas], DIMENSIONES[columnas])
    st.plotly_chart(graficos.mapa_calor(
        tasa, lineas, f"Tasa de pérdida (%): {filas.lower()} × {columnas.lower()}",
        eje_x=columnas, eje_y=filas))
    st.caption("Las celdas vacías son combinaciones sin ventas. Pasá el cursor para ver cuántas "
               "líneas hay detrás de cada porcentaje: con pocas líneas la tasa es poco fiable.")
else:
    st.info("Elegí una segunda dimensión para ver el cruce en un mapa de calor. "
            "Probá **Región × Descuento**: la diferencia entre regiones se explica por el descuento.",
            icon="💡")
