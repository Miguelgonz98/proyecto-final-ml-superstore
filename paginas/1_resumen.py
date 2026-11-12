import streamlit as st

from src import graficos
from src.datos import obtener_datos, serie_mensual
from src.filtros import aplicar_filtros
from src.formato import dolares, dolares_compacto, numero, porcentaje

st.title("Resumen")
st.caption("¿Qué líneas de pedido de la tienda generan pérdida? Usá los filtros de la barra lateral.")

df = aplicar_filtros(obtener_datos())

perdidas = df.loc[df["Profit"] < 0, "Profit"]
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Líneas", numero(len(df)), help="Líneas de pedido.")
k2.metric("Con pérdida", porcentaje(df["Pérdida"].mean() * 100),
          help="Porcentaje de líneas con ganancia negativa.")
k3.metric("Ventas", dolares_compacto(df["Sales"].sum()), help=dolares(df["Sales"].sum()))
k4.metric("Ganancia", dolares_compacto(df["Profit"].sum()), help=dolares(df["Profit"].sum()))
k5.metric("Monto perdido", dolares_compacto(-perdidas.sum()),
          help=f"{dolares(-perdidas.sum())}: suma de la ganancia negativa de las líneas con pérdida.")

izquierda, derecha = st.columns([3, 2])
izquierda.plotly_chart(graficos.lineas_mensuales(serie_mensual(df)))
derecha.plotly_chart(graficos.barras_ganancia(df))
