"""Modelo final del notebook: regresión logística dentro de un Pipeline."""
from types import SimpleNamespace

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from src.datos import cargar_datos

RANDOM_STATE = 42
VARIABLES_NUMERICAS = ["Quantity", "Discount"]
VARIABLE_ASIMETRICA = ["Sales"]
VARIABLES_CATEGORICAS = ["Ship Mode", "Segment", "Region", "Category", "Sub-Category"]
PREDICTORAS = VARIABLES_NUMERICAS + VARIABLE_ASIMETRICA + VARIABLES_CATEGORICAS
OBJETIVO = "Pérdida"
DESCUENTO_REGLA = 0.3  # regla de negocio: descuento ≥ 30 %


def crear_pipeline(modelo) -> Pipeline:
    preprocesador = ColumnTransformer([
        ("numericas", Pipeline([
            ("imputar", SimpleImputer(strategy="median")),
            ("escalar", StandardScaler()),
        ]), VARIABLES_NUMERICAS),
        ("ventas", Pipeline([
            ("imputar", SimpleImputer(strategy="median")),
            ("log", FunctionTransformer(np.log1p, feature_names_out="one-to-one")),
            ("escalar", StandardScaler()),
        ]), VARIABLE_ASIMETRICA),
        ("categoricas", Pipeline([
            ("imputar", SimpleImputer(strategy="most_frequent")),
            ("codificar", OneHotEncoder(handle_unknown="ignore")),
        ]), VARIABLES_CATEGORICAS),
    ], verbose_feature_names_out=False)
    return Pipeline([("preprocesamiento", preprocesador), ("modelo", modelo)])


@st.cache_resource(show_spinner="Entrenando el modelo…")
def entrenar_modelo() -> SimpleNamespace:
    """Entrena con la misma división del notebook y guarda lo necesario para evaluar."""
    df = cargar_datos()
    X, y = df[PREDICTORAS], df[OBJETIVO]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE)

    logistica = crear_pipeline(LogisticRegression(
        max_iter=1000, class_weight="balanced", random_state=RANDOM_STATE)).fit(X_train, y_train)
    dummy = crear_pipeline(DummyClassifier(strategy="most_frequent")).fit(X_train, y_train)

    return SimpleNamespace(
        pipeline=logistica,
        n_train=len(X_train),
        n_test=len(X_test),
        y_test=y_test.to_numpy(),
        prob_test=logistica.predict_proba(X_test)[:, 1],
        pred_dummy=dummy.predict(X_test),
        pred_regla=(X_test["Discount"] >= DESCUENTO_REGLA).astype(int).to_numpy(),
        ganancia_test=df.loc[X_test.index, "Profit"].to_numpy(),
    )


def evaluar(y_real: np.ndarray, y_pred: np.ndarray, ganancia: np.ndarray) -> dict:
    """Matriz de confusión, métricas de la clase «pérdida» y monto de pérdidas no detectadas."""
    vp = int(((y_real == 1) & (y_pred == 1)).sum())
    vn = int(((y_real == 0) & (y_pred == 0)).sum())
    fp = int(((y_real == 0) & (y_pred == 1)).sum())
    es_fn = (y_real == 1) & (y_pred == 0)
    fn = int(es_fn.sum())
    recall = vp / (vp + fn) if vp + fn else 0.0
    precision = vp / (vp + fp) if vp + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    monto = float(-ganancia[es_fn].sum())
    total = float(-ganancia[y_real == 1].sum())
    return {
        "vp": vp, "vn": vn, "fp": fp, "fn": fn,
        "recall": recall, "precision": precision, "f1": f1,
        "accuracy": (vp + vn) / len(y_real),
        "monto_no_detectado": monto,
        "pct_no_detectado": monto / total * 100 if total else 0.0,
    }


def evaluar_umbral(modelo: SimpleNamespace, umbral: float) -> dict:
    return evaluar(modelo.y_test, (modelo.prob_test >= umbral).astype(int), modelo.ganancia_test)


@st.cache_data
def curva_por_umbral(_modelo: SimpleNamespace) -> pd.DataFrame:
    """Recall, precisión y F1 para cada umbral entre 0,05 y 0,95."""
    filas = []
    for umbral in np.round(np.arange(0.05, 0.951, 0.01), 2):
        r = evaluar_umbral(_modelo, umbral)
        filas.append({"umbral": umbral, "Recall": r["recall"], "Precisión": r["precision"], "F1": r["f1"]})
    return pd.DataFrame(filas)


def probabilidad_perdida(modelo: SimpleNamespace, ventas: pd.DataFrame) -> np.ndarray:
    return modelo.pipeline.predict_proba(ventas[PREDICTORAS])[:, 1]
