# Superstore · Riesgo de pérdida

App interactiva de Streamlit que explora qué líneas de pedido de una tienda minorista
generan pérdida (`Profit < 0`) y estima ese riesgo con un modelo de clasificación.
Es la versión interactiva de mi proyecto final de Machine Learning.

## Qué hace

| Página | Qué se puede explorar |
| --- | --- |
| **Resumen** | KPIs, ventas y ganancia por mes, ganancia por subcategoría |
| **Explorar el riesgo** | Tasa de pérdida por la dimensión que elijas y cruce de dos dimensiones en un mapa de calor |
| **Descuento y pérdida** | Tasa de pérdida por nivel de descuento, por categoría o subcategoría |
| **Simulador** | Armás una venta y ves la probabilidad de pérdida y cómo cambia con el descuento |
| **Desempeño del modelo** | Matriz de confusión con umbral ajustable, comparada con la regla «descuento ≥ 30 %» y un `DummyClassifier` |

Los filtros de la barra lateral (categoría, región, segmento y años) afectan a las tres
primeras páginas. El modelo es una regresión logística (`class_weight="balanced"`) dentro
de un `Pipeline` de scikit-learn; se entrena al arrancar la app, en menos de 2 segundos.

## Cómo correrla localmente

Requiere Python 3.11, 3.12 o 3.13.

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

```
app.py            navegación y filtros globales
paginas/          una página por archivo
src/              carga de datos, modelo, filtros y gráficos
data/             Sample - Superstore.csv
```

## Datos

[Superstore Dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final),
publicado en Kaggle por Vivek Chowdhury (vivek468). Es el conjunto de ejemplo
*Sample - Superstore* de Tableau, publicado solo con fines educativos.

**Los datos son ficticios:** no corresponden a una tienda, a clientes ni a ventas reales.
