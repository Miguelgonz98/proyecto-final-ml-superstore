import streamlit as st

from src import graficos
from src.datos import obtener_datos, tasa_por
from src.filtros import aplicar_filtros
from src.formato import numero, porcentaje

st.title("Descuento y pérdida")
st.caption("El descuento es la señal más fuerte: mirá cómo se mueve el umbral según el producto.")

df = aplicar_filtros(obtener_datos())

control, selector = st.columns(2)
alcance = control.radio("Ver", ["Todo", "Categoría", "Subcategoría"], horizontal=True)
seleccion = df
nombre = "todas las líneas"
if alcance != "Todo":
    columna = "Category" if alcance == "Categoría" else "Sub-Category"
    valor = selector.selectbox(alcance, sorted(df[columna].unique()))
    seleccion = df[df[columna] == valor]
    nombre = valor


def zona(datos, mascara, titulo, contenedor):
    parte = datos[mascara]
    if parte.empty:
        contenedor.metric(titulo, "Sin ventas")
    else:
        contenedor.metric(titulo, porcentaje(parte["Pérdida"].mean() * 100),
                          help=f"{numero(len(parte))} líneas, {numero(parte['Pérdida'].sum())} con pérdida.")


z1, z2, z3, z4 = st.columns(4)
zona(seleccion, seleccion["Discount"] == 0, "Sin descuento", z1)
zona(seleccion, (seleccion["Discount"] > 0) & (seleccion["Discount"] < 0.2), "Descuento de 10-15 %", z2)
zona(seleccion, seleccion["Discount"] == 0.2, "Descuento de 20 %", z3)
zona(seleccion, seleccion["Discount"] >= 0.3, "Descuento ≥ 30 %", z4)

tabla = tasa_por(seleccion, "Descuento")
tasa_seleccion = seleccion["Pérdida"].mean() * 100
st.plotly_chart(graficos.barras_tasa(
    tabla, "Descuento", tasa_seleccion, f"Tasa de pérdida por nivel de descuento — {nombre}",
    etiqueta_global=f"Tasa de {nombre}"))

sobre_mitad = tabla[tabla["tasa"] >= 50]
if sobre_mitad.empty:
    st.success(f"En **{nombre}** ningún nivel de descuento llega al 50 % de líneas con pérdida.", icon="✅")
else:
    st.error(f"En **{nombre}**, la mayoría de las líneas pierde a partir de un descuento de "
             f"**{sobre_mitad['Descuento'].iloc[0]}**.", icon="⚠️")

st.plotly_chart(graficos.barras_lineas(tabla, "Descuento", "Cuántas líneas hay en cada nivel"))
