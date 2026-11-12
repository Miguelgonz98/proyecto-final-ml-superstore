import numpy as np
import pandas as pd
import streamlit as st

from src import graficos
from src.datos import obtener_datos
from src.formato import numero, porcentaje
from src.modelo import entrenar_modelo, probabilidad_perdida

UMBRAL = 0.5

st.title("Simulador de una venta")
st.caption("Armá una línea de pedido y mirá la probabilidad de pérdida que estima el modelo.")

df = obtener_datos()
modelo = entrenar_modelo()
categoria_de = df.drop_duplicates("Sub-Category").set_index("Sub-Category")["Category"]

entradas, resultado = st.columns([1, 2], gap="large")

with entradas:
    subcategoria = st.selectbox("Subcategoría", sorted(df["Sub-Category"].unique()),
                                index=sorted(df["Sub-Category"].unique()).index("Tables"))
    st.caption(f"Categoría: {categoria_de[subcategoria]}")
    region = st.selectbox("Región", sorted(df["Region"].unique()))
    segmento = st.selectbox("Segmento", sorted(df["Segment"].unique()))
    envio = st.selectbox("Modo de envío", sorted(df["Ship Mode"].unique()),
                         index=sorted(df["Ship Mode"].unique()).index("Standard Class"))
    cantidad = st.slider("Cantidad", 1, int(df["Quantity"].max()), 3)
    descuento = st.slider("Descuento (%)", 0, 80, 20, step=5) / 100
    mediana = float(df.loc[df["Sub-Category"] == subcategoria, "Sales"].median())
    ventas = st.number_input(
        "Monto de la venta (USD)", min_value=1.0, value=round(mediana, 2), step=10.0,
        key=f"ventas_{subcategoria}",
        help="El modelo también usa el monto de la línea. Por defecto se propone la mediana de la "
             "subcategoría; en el notebook se comprobó que casi no cambia la predicción.")

venta = {"Quantity": cantidad, "Discount": descuento, "Sales": ventas, "Ship Mode": envio,
         "Segment": segmento, "Region": region, "Category": categoria_de[subcategoria],
         "Sub-Category": subcategoria}
probabilidad = float(probabilidad_perdida(modelo, pd.DataFrame([venta]))[0])

descuentos = np.arange(0, 0.801, 0.01)
barrido = pd.DataFrame([venta] * len(descuentos)).assign(Discount=descuentos)
curva = probabilidad_perdida(modelo, barrido)

with resultado:
    st.plotly_chart(graficos.medidor(probabilidad, UMBRAL))
    if probabilidad >= UMBRAL:
        st.error("**Riesgo alto:** el modelo marcaría esta venta como pérdida.", icon="🔴")
    else:
        st.success("**Riesgo bajo:** el modelo marcaría esta venta como rentable.", icon="🟢")

    cruces = descuentos[curva >= UMBRAL]
    if len(cruces) == 0:
        st.caption("Con esta combinación, la probabilidad no llega al 50 % con ningún descuento de 0 a 80 %.")
    elif cruces[0] == 0:
        st.caption("Con esta combinación, la probabilidad supera el 50 % incluso sin descuento.")
    else:
        st.caption(f"Con esta combinación, la probabilidad cruza el 50 % a partir de un descuento "
                   f"de **{cruces[0] * 100:.0f} %**.")

st.plotly_chart(graficos.curva_descuento(descuentos, curva, descuento, probabilidad, UMBRAL))

similares = df[(df["Sub-Category"] == subcategoria) & (df["Discount"].round(2) == round(descuento, 2))]
if len(similares):
    st.caption(f"En el historial hay {numero(len(similares))} líneas de {subcategoria} con "
               f"{descuento * 100:.0f} % de descuento: el {porcentaje(similares['Pérdida'].mean() * 100)} "
               "generó pérdida.")
else:
    st.caption(f"En el historial no hay líneas de {subcategoria} con {descuento * 100:.0f} % de "
               "descuento: la estimación es una extrapolación del modelo.")
