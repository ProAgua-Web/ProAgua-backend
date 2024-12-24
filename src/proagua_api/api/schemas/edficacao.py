from typing import Optional, List

from ninja import Schema, FilterSchema, Field
from django.urls import reverse_lazy
from .image import ImageOut

class EdificacaoIn(Schema):
    codigo: str
    nome: str
    campus: str 
    cronograma: int
    informacoes_gerais: Optional[str] = None


class EdificacaoOut(Schema):
    codigo: str
    nome: str
    campus: str 
    cronograma: int
    # pontos_url: str
    imagens: List[ImageOut]
    informacoes_gerais: Optional[str] = None
    
    @staticmethod
    def resolve_pontos_url(obj):
        return str(reverse_lazy("api-1.0.0:list_pontos", kwargs={"cod_edificacao": obj.codigo}))
    


class FilterEdificacao(FilterSchema):
    q: Optional[str] = Field(None, q=['nome__contains', 'codigo__contains'])
    cronograma__gte: Optional[int] = None
    cronograma__lte: Optional[int] = None
    campus: Optional[str] = None
