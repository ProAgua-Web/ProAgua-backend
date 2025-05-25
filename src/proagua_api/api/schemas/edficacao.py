from typing import Optional, List

from ninja import Schema, FilterSchema, Field
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
    imagens: List[ImageOut]
    informacoes_gerais: Optional[str] = None


class FilterEdificacao(FilterSchema):
    q: Optional[str] = Field(None, q=['nome__icontains', 'codigo__icontains']) # type: ignore
    cronograma__gte: Optional[int] = None
    cronograma__lte: Optional[int] = None
    campus: Optional[str] = None
