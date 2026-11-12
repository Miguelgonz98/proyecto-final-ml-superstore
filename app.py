"""Punto de entrada: navegación entre páginas y filtros globales."""
import streamlit as st

from src.datos import obtener_datos
from src.filtros import barra_filtros

st.set_page_config(page_title="Superstore · Riesgo de pérdida", page_icon="📉", layout="wide")

paginas_con_filtros = [
    st.Page("paginas/1_resumen.py", title="Resumen", icon="📊", default=True),
    st.Page("paginas/2_explorar_riesgo.py", title="Explorar el riesgo", icon="🔎"),
    st.Page("paginas/3_descuento.py", title="Descuento y pérdida", icon="🏷️"),
]
paginas_del_modelo = [
    st.Page("paginas/4_simulador.py", title="Simulador", icon="🎛️"),
    st.Page("paginas/5_desempeno.py", title="Desempeño del modelo", icon="🎯"),
]

pagina = st.navigation({"Análisis": paginas_con_filtros, "Modelo": paginas_del_modelo})

datos = obtener_datos()
barra_filtros(datos, activos=pagina in paginas_con_filtros)
st.sidebar.caption("Datos ficticios: *Sample - Superstore* (Tableau), 2014-2017.")

pagina.run()
