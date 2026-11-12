import streamlit as st

from src import graficos
from src.formato import dolares, numero, porcentaje
from src.modelo import curva_por_umbral, entrenar_modelo, evaluar, evaluar_umbral

st.title("Desempeño del modelo")

modelo = entrenar_modelo()
st.caption(f"Regresión logística entrenada con {numero(modelo.n_train)} líneas y evaluada en "
           f"{numero(modelo.n_test)} líneas de prueba que no vio durante el entrenamiento.")

umbral = st.slider(
    "Umbral de decisión", 0.05, 0.95, 0.50, step=0.01,
    help="Probabilidad a partir de la cual una línea se marca como pérdida. Bajarlo detecta más "
         "pérdidas (más recall) a costa de más falsas alarmas (menos precisión).")

r = evaluar_umbral(modelo, umbral)
base = evaluar_umbral(modelo, 0.5)


def delta(clave, decimales=3):
    """Diferencia frente al umbral 0,5 (no se muestra cuando el umbral es 0,5)."""
    if abs(umbral - 0.5) < 1e-9:
        return None
    diferencia = r[clave] - base[clave]
    return f"{diferencia:+.{decimales}f}".replace(".", ",")


matriz, metricas = st.columns([3, 2], gap="large")
matriz.plotly_chart(graficos.matriz_confusion(r))

with metricas:
    a, b = st.columns(2)
    a.metric("Falsos negativos", numero(r["fn"]), delta("fn", 0), delta_color="inverse",
             help="Pérdidas que el modelo no detectó.")
    b.metric("Falsos positivos", numero(r["fp"]), delta("fp", 0), delta_color="inverse",
             help="Ventas rentables marcadas como pérdida.")
    a.metric("Recall", numero(r["recall"], 3), delta("recall"))
    b.metric("Precisión", numero(r["precision"], 3), delta("precision"))
    a.metric("F1", numero(r["f1"], 3), delta("f1"))
    b.metric("Sin detectar (USD)", dolares(r["monto_no_detectado"]),
             help=f"Monto de las pérdidas no detectadas. Equivale al {porcentaje(r['pct_no_detectado'], 2)} del monto total de pérdidas "
                  "del conjunto de prueba.")
    if delta("f1"):
        st.caption("Las flechas comparan contra el umbral 0,50.")

st.plotly_chart(graficos.curvas_umbral(curva_por_umbral(modelo), umbral))

st.subheader("¿Le gana a las referencias?")
resultados = {
    f"Modelo (umbral {umbral:.2f})".replace(".", ","): r,
    "Regla: descuento ≥ 30 %": evaluar(modelo.y_test, modelo.pred_regla, modelo.ganancia_test),
    "Dummy (clase mayoritaria)": evaluar(modelo.y_test, modelo.pred_dummy, modelo.ganancia_test),
}
izquierda, derecha = st.columns(2)
izquierda.plotly_chart(graficos.comparacion_metricas(resultados))
derecha.plotly_chart(graficos.comparacion_monto(resultados))
