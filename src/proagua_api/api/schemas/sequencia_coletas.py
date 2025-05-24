from typing import Optional, List
from datetime import datetime

from ninja import Field, FilterSchema, Schema
from django.urls import reverse

from .coleta import ColetaOut
from .ponto_coleta import PontoColetaOut
from ...models import SequenciaColetas


class SequenciaColetasIn(Schema):
    amostragem: int
    ponto_id: int


class SequenciaColetasOut(Schema):
    id: int
    amostragem: int
    ponto: PontoColetaOut
    quantidade_coletas: int = None
    status: Optional[bool] = None
    status_message: Optional[str] = None
    # ultima_coleta: Optional[datetime] = None
    
    # @staticmethod
    # def resolve_coletas_url(obj):
    #     return reverse("api-1.0.0:list_coletas_sequencia", kwargs={"id_sequencia": obj.id})

    # @staticmethod
    # def resolve_ultima_coleta(obj: SequenciaColetas):
    #     last = obj.coletas.order_by("data").last()
    #     if last:
    #         return last.data


class FilterSequenciaColetas(FilterSchema):
    q: Optional[str] = Field( 
        default=None,
        q=[
            "ponto__localizacao__contains",
            "ponto__edificacao__nome__contains",
            "ponto__edificacao__codigo__contains"
        ],
        description="Campo de pesquisa por localização ou nome de edificação"
    ) # type: ignore

    amostragem: Optional[int] = Field(
        default=None,
        alias="amostragem"
    )

    ponto__id: Optional[int] = Field(
        default=None,
        alias="ponto_id"
    )

    ponto__edificacao__campus: Optional[str] = Field(
        default=None,
        alias="campus"
    )

    status: Optional[bool] = Field(
        default=None,
        alias="status"
    )
