"""Gráficos de Plotly con una paleta única: rojo = pérdida, verde = rentable."""
import pandas as pd
import plotly.graph_objects as go

ROJO = "#D1495B"       # pérdida
VERDE = "#2A9D8F"      # rentable
AZUL = "#3D5A80"       # medidas neutras (ventas, cantidad de líneas)
GRIS = "#8D99AE"       # referencias
ESCALA_ROJOS = [[0, "#FDF1F0"], [0.5, "#EE9A9A"], [1, "#A4243B"]]


def _miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _estilo(fig: go.Figure, titulo: str, alto: int = 420) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, font=dict(size=16)),
        height=alto,
        margin=dict(l=10, r=10, t=60, b=10),
        separators=",.",
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1),
        hoverlabel=dict(font_size=13),
    )
    return fig


def lineas_mensuales(mensual: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for columna, nombre, color in [("Sales", "Ventas", AZUL), ("Profit", "Ganancia", VERDE)]:
        fig.add_trace(go.Scatter(
            x=mensual["Order Date"], y=mensual[columna], name=nombre, mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=nombre + ": $ %{y:,.0f}<extra></extra>",
        ))
    fig.add_hline(y=0, line_color=GRIS, line_width=1)
    fig.update_layout(hovermode="x unified", yaxis_title="USD", xaxis_hoverformat="%b %Y")
    return _estilo(fig, "Ventas y ganancia por mes")


def barras_ganancia(df: pd.DataFrame, columna: str = "Sub-Category") -> go.Figure:
    tabla = df.groupby(columna)["Profit"].sum().sort_values()
    fig = go.Figure(go.Bar(
        x=tabla.values, y=tabla.index, orientation="h",
        marker_color=[ROJO if v < 0 else VERDE for v in tabla.values],
        hovertemplate="%{y}: $ %{x:,.0f}<extra></extra>",
    ))
    fig.add_vline(x=0, line_color=GRIS, line_width=1)
    fig.update_layout(xaxis_title="Ganancia total (USD) · rojo = pérdida neta")
    return _estilo(fig, "Ganancia por subcategoría", alto=480)


def barras_tasa(tabla: pd.DataFrame, columna: str, tasa_global: float, titulo: str,
                horizontal: bool = False, etiqueta_global: str = "Tasa global") -> go.Figure:
    """Tasa de pérdida por grupo; rojo si supera la referencia, verde si no."""
    colores = [ROJO if t > tasa_global else VERDE for t in tabla["tasa"]]
    comun = dict(
        marker_color=colores, customdata=tabla[["lineas", "perdidas"]],
        text=[f"{t:.1f} %".replace(".", ",") for t in tabla["tasa"]], textposition="outside",
        cliponaxis=False,
    )
    plantilla = ("<b>%{" + ("y" if horizontal else "x") + "}</b><br>Tasa de pérdida: %{"
                 + ("x" if horizontal else "y") + ":.1f} %<br>"
                 "Líneas: %{customdata[0]:,}<br>Con pérdida: %{customdata[1]:,}<extra></extra>")
    nota = f"{etiqueta_global}: {tasa_global:.1f} %".replace(".", ",")
    if horizontal:
        fig = go.Figure(go.Bar(x=tabla["tasa"], y=tabla[columna], orientation="h",
                               hovertemplate=plantilla, **comun))
        fig.add_vline(x=tasa_global, line_dash="dash", line_color=GRIS,
                      annotation_text=nota, annotation_position="top")
        fig.update_layout(xaxis=dict(title="Líneas con pérdida (%)", range=[0, 112]))
        alto = max(360, 28 * len(tabla) + 120)
    else:
        fig = go.Figure(go.Bar(x=tabla[columna], y=tabla["tasa"], hovertemplate=plantilla, **comun))
        fig.add_hline(y=tasa_global, line_dash="dash", line_color=GRIS,
                      annotation_text=nota, annotation_position="top left")
        fig.update_layout(yaxis=dict(title="Líneas con pérdida (%)", range=[0, 112]),
                          xaxis=dict(type="category"))
        alto = 440
    return _estilo(fig, titulo, alto=alto)


def barras_lineas(tabla: pd.DataFrame, columna: str, titulo: str) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=tabla[columna], y=tabla["lineas"], marker_color=AZUL,
        hovertemplate="<b>%{x}</b><br>Líneas: %{y:,}<extra></extra>",
    ))
    fig.update_layout(yaxis_title="Líneas de pedido", xaxis=dict(type="category"))
    return _estilo(fig, titulo, alto=260)


def mapa_calor(tasa: pd.DataFrame, lineas: pd.DataFrame, titulo: str,
               eje_x: str, eje_y: str) -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=tasa.values, x=[str(c) for c in tasa.columns], y=[str(i) for i in tasa.index],
        customdata=lineas.reindex_like(tasa).fillna(0).values,
        colorscale=ESCALA_ROJOS, zmin=0, zmax=100, xgap=2, ygap=2,
        texttemplate="%{z:.0f}", hoverongaps=False,
        colorbar=dict(title="% pérdida", ticksuffix=" %"),
        hovertemplate=(f"{eje_y}: <b>%{{y}}</b><br>{eje_x}: <b>%{{x}}</b><br>"
                       "Tasa de pérdida: %{z:.1f} %<br>Líneas: %{customdata:,}<extra></extra>"),
    ))
    fig.update_layout(xaxis=dict(title=eje_x, type="category", side="bottom"),
                      yaxis=dict(title=eje_y, type="category", autorange="reversed"),
                      plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    return _estilo(fig, titulo, alto=max(380, 30 * len(tasa) + 160))


def medidor(probabilidad: float, umbral: float = 0.5) -> go.Figure:
    color = ROJO if probabilidad >= umbral else VERDE
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=probabilidad * 100,
        number=dict(suffix=" %", valueformat=".1f", font=dict(color=color, size=54)),
        gauge=dict(
            axis=dict(range=[0, 100], ticksuffix=" %"),
            bar=dict(color=color, thickness=0.75),
            steps=[dict(range=[0, umbral * 100], color="rgba(42,157,143,0.15)"),
                   dict(range=[umbral * 100, 100], color="rgba(209,73,91,0.15)")],
            threshold=dict(line=dict(color=GRIS, width=3), thickness=0.9, value=umbral * 100),
        ),
    ))
    return _estilo(fig, "Probabilidad de pérdida estimada", alto=320)


def curva_descuento(descuentos, probabilidades, descuento_actual: float,
                    prob_actual: float, umbral: float = 0.5) -> go.Figure:
    fig = go.Figure()
    fig.add_hrect(y0=umbral * 100, y1=100, fillcolor=ROJO, opacity=0.07, line_width=0)
    fig.add_hrect(y0=0, y1=umbral * 100, fillcolor=VERDE, opacity=0.07, line_width=0)
    fig.add_trace(go.Scatter(
        x=[d * 100 for d in descuentos], y=[p * 100 for p in probabilidades], mode="lines",
        line=dict(color=AZUL, width=2), name="Probabilidad estimada",
        hovertemplate="Descuento %{x:.0f} %<br>Probabilidad de pérdida: %{y:.1f} %<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[descuento_actual * 100], y=[prob_actual * 100], mode="markers", name="Venta simulada",
        marker=dict(size=14, color=ROJO if prob_actual >= umbral else VERDE,
                    line=dict(color="white", width=2)),
        hovertemplate="Venta simulada<br>Descuento %{x:.0f} %<br>Probabilidad: %{y:.1f} %<extra></extra>",
    ))
    fig.add_hline(y=umbral * 100, line_dash="dash", line_color=GRIS,
                  annotation_text="Umbral 50 %: desde aquí se marca como pérdida",
                  annotation_position="top left")
    fig.update_layout(xaxis=dict(title="Descuento (%)", range=[-2, 82], ticksuffix=" %"),
                      yaxis=dict(title="Probabilidad de pérdida (%)", range=[-3, 103]),
                      showlegend=False)
    return _estilo(fig, "Cómo cambia la probabilidad al mover el descuento", alto=400)


def matriz_confusion(r: dict) -> go.Figure:
    """Filas = clase real, columnas = clase predicha. Verde = acierto, rojo = error."""
    textos = [[f"<b>{_miles(r['vn'])}</b><br>Verdaderos negativos", f"<b>{_miles(r['fp'])}</b><br>Falsos positivos"],
              [f"<b>{_miles(r['fn'])}</b><br>Falsos negativos", f"<b>{_miles(r['vp'])}</b><br>Verdaderos positivos"]]
    fig = go.Figure(go.Heatmap(
        z=[[1, 0], [0, 1]], x=["Predicho: rentable", "Predicho: pérdida"],
        y=["Real: rentable", "Real: pérdida"], text=textos, texttemplate="%{text}",
        textfont=dict(size=16, color="#1B1B1B"),
        colorscale=[[0, "#F4B6BD"], [1, "#A9DCD5"]], showscale=False, xgap=4, ygap=4,
        hoverinfo="skip",
    ))
    fig.update_layout(yaxis=dict(autorange="reversed"), xaxis=dict(side="top"),
                      plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig = _estilo(fig, "", alto=360)
    fig.update_layout(margin=dict(t=40))
    return fig


def curvas_umbral(curva: pd.DataFrame, umbral: float) -> go.Figure:
    fig = go.Figure()
    for nombre, color, trazo in [("Recall", ROJO, "solid"), ("Precisión", AZUL, "solid"), ("F1", "#1B1B1B", "dot")]:
        fig.add_trace(go.Scatter(
            x=curva["umbral"], y=curva[nombre], name=nombre, mode="lines",
            line=dict(color=color, width=2, dash=trazo),
            hovertemplate=nombre + ": %{y:.3f}<extra></extra>",
        ))
    fig.add_vline(x=umbral, line_dash="dash", line_color=GRIS,
                  annotation_text="Umbral elegido", annotation_position="bottom right")
    fig.update_layout(hovermode="x unified", xaxis=dict(title="Umbral de decisión", tickformat=".2f"),
                      yaxis=dict(range=[0, 1.02], tickformat=".1f"))
    return _estilo(fig, "Recall, precisión y F1 según el umbral", alto=360)


def comparacion_metricas(resultados: dict) -> go.Figure:
    """`resultados`: nombre del clasificador -> dict de `evaluar`."""
    colores = dict(zip(resultados, [VERDE, AZUL, GRIS]))
    metricas = [("recall", "Recall"), ("precision", "Precisión"), ("f1", "F1")]
    fig = go.Figure()
    for nombre, r in resultados.items():
        valores = [r[clave] for clave, _ in metricas]
        fig.add_trace(go.Bar(
            x=[etiqueta for _, etiqueta in metricas], y=valores, name=nombre,
            marker_color=colores[nombre],
            text=[f"{v:.3f}".replace(".", ",") for v in valores], textposition="outside",
            hovertemplate=nombre + "<br>%{x}: %{y:.3f}<extra></extra>",
        ))
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.08,
                      yaxis=dict(range=[0, 1.12], tickformat=".1f"))
    return _estilo(fig, "Métricas en el conjunto de prueba", alto=400)


def comparacion_monto(resultados: dict) -> go.Figure:
    nombres = list(resultados)
    montos = [resultados[n]["monto_no_detectado"] for n in nombres]
    fig = go.Figure(go.Bar(
        x=montos, y=nombres, orientation="h", marker_color=ROJO,
        customdata=[[resultados[n]["fn"], resultados[n]["pct_no_detectado"]] for n in nombres],
        text=[f"$ {m:,.0f}".replace(",", ".") for m in montos], textposition="outside",
        cliponaxis=False,
        hovertemplate=("<b>%{y}</b><br>Pérdida no detectada: $ %{x:,.0f}<br>"
                       "Falsos negativos: %{customdata[0]}<br>"
                       "% de la pérdida total: %{customdata[1]:.1f} %<extra></extra>"),
    ))
    fig.update_layout(xaxis=dict(title="USD", range=[0, max(montos) * 1.2 or 1]),
                      yaxis=dict(autorange="reversed"))
    return _estilo(fig, "Pérdidas no detectadas (USD)", alto=400)
