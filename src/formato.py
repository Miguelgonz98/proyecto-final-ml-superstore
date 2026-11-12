"""Formato de números en español (coma decimal, punto de miles)."""


def numero(valor: float, decimales: int = 0) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".")


def porcentaje(valor: float, decimales: int = 1) -> str:
    """`valor` ya está en escala 0-100."""
    return f"{numero(valor, decimales)} %"


def dolares(valor: float, decimales: int = 0) -> str:
    signo = "-" if valor < 0 else ""
    return f"{signo}$ {numero(abs(valor), decimales)}"


def dolares_compacto(valor: float) -> str:
    """Montos grandes abreviados para las tarjetas: $ 2,30 M, $ 286 mil."""
    signo = "-" if valor < 0 else ""
    absoluto = abs(valor)
    if absoluto >= 1e6:
        return f"{signo}$ {numero(absoluto / 1e6, 2)} M"
    if absoluto >= 1e4:
        return f"{signo}$ {numero(absoluto / 1e3, 0)} mil"
    return dolares(valor)
