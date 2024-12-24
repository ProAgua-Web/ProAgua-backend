from ninja import Schema

from typing import Optional


class ParametrosReferenciaIn(Schema):
    min_temperatura: Optional[float] = None
    max_temperatura: Optional[float] = None
    min_cloro_residual_livre: Optional[float] = None
    max_cloro_residual_livre: Optional[float] = None
    min_turbidez: Optional[float] = None
    max_turbidez: Optional[float] = None
    min_cor: Optional[float] = None
    max_cor: Optional[float] = None
    coliformes_totais: bool
    escherichia: bool

class ParametrosReferenciaOut(Schema):
    min_temperatura: Optional[float] = None
    max_temperatura: Optional[float] = None
    min_cloro_residual_livre: Optional[float] = None
    max_cloro_residual_livre: Optional[float] = None
    min_turbidez: Optional[float] = None
    max_turbidez: Optional[float] = None
    min_cor: Optional[float] = None
    max_cor: Optional[float] = None
    coliformes_totais: Optional[bool] = None
    escherichia: Optional[bool] = None
