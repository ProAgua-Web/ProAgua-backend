from typing import List, Optional
from datetime import date, datetime

from ninja import Schema, FilterSchema, Field
from django.urls import reverse

from ... import models
from .ponto_coleta import PontoColetaOut

class ColetaIn(Schema):
    sequencia_id: int
    ponto_id: int
    temperatura: float
    cloro_residual_livre: float
    turbidez: float
    coliformes_totais: bool
    escherichia: bool
    cor: float
    data: datetime
    responsavel: List[int]
    ordem: str


class ColetaOut(Schema):
    id: int
    temperatura: float
    cloro_residual_livre: float
    turbidez: float
    coliformes_totais: bool
    escherichia: bool
    cor: float
    data: datetime
    responsaveis_id: List[int]
    ordem: str
    sequencia_id: int
    ponto: PontoColetaOut
    status: Optional[bool] = None
    # status_messages: Optional[List[str]] = None

    @staticmethod
    def resolve_responsaveis_id(obj: models.Coleta):
        return [r.id for r in obj.responsavel.all()]

    # @staticmethod
    # def resolve_status_messages(obj: models.Coleta):
    #     return obj.analise()["messages"]


class FilterColeta(FilterSchema):
    responsavel: Optional[str] = Field( 
        default=None,
        q=[
            'responsavel__username__icontains',
            'responsavel__first_name__icontains',
            'responsavel__last_name__icontains'
        ]
    ) # type: ignore
    
    data__gte: Optional[date] = Field(
        default=None,
        alias="data_minima"
    )
    
    data__lte: Optional[date] = Field(
        default=None,
        alias="data_maxima"
    )
    
    sequencia__id: Optional[int] = Field(
        default=None,
        alias="sequencia_id"
    )
    
    temperatura__gte: Optional[float] = Field(
        default=None,
        alias="temperatura_minima"
    )
    
    temperatura__lte: Optional[float] = Field(
        default=None,
        alias="temperatura_maxima"
    )
    
    cloro_residual_livre__gte: Optional[float] = Field(
        default=None,
        alias="cloro_residual_livre_minimo"
    )
    
    cloro_residual_livre__lte: Optional[float] = Field(
        default=None,
        alias="cloro_residual_livre_maximo"
    )
    
    turbidez__gte: Optional[float] = Field(
        default=None,
        alias="turbidez_minima"
    )
    
    turbidez__lte: Optional[float] = Field(
        default=None,
        alias="turbidez_maxima"
    )
    
    coliformes_totais: Optional[bool] = Field(
        default=None,
        alias="coliformes_totais"
    )
    
    escherichia: Optional[bool] = Field(
        default=None,
        alias="escherichia"
    )
    
    cor__gte: Optional[float] = Field(
        default=None,
        alias="cor_minima"
    )
    
    cor__lte: Optional[float] = Field(
        default=None,
        alias="cor_maxima"
    )
    
    ordem: Optional[str] = Field(
        default=None,
        alias="ordem"
    )

    ponto__edificacao__codigo__exact: Optional[str] = Field(
        default=None,
        alias="codigo_edificacao"
    )
    
    ponto__id: Optional[int] = Field(
        default=None,
        alias="ponto_id"
    )