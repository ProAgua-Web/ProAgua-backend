from typing import Optional, List

from ninja import Schema, FilterSchema, Field
from .edficacao import EdificacaoOut
from .image import ImageOut


class PontoColetaIn(Schema):
    codigo_edificacao: str
    tipo: int
    localizacao: Optional[str] = None
    amontante_id: Optional[int] = None
    observacao: Optional[str] = None
    tombo: Optional[str] = None
    quantidade: Optional[int] = None # unico, duplo, triplo
    capacidade: Optional[int] = None
    material: Optional[str] = None
    fonte_informacao: Optional[str] = None


class PontoColetaOut(Schema):
    id: int
    edificacao: EdificacaoOut
    tipo: int
    localizacao: Optional[str] = None
    amontante: Optional['PontoColetaOut'] = None
    imagens: List[ImageOut]
    tombo: Optional[str] = None
    quantidade: Optional[int] = None # unico, duplo, triplo
    capacidade: Optional[int] = None
    observacao: Optional[str] = None
    material: Optional[str] = None
    fonte_informacao: Optional[str] = None
    # status: Optional[bool] = None


class FilterPontos(FilterSchema):
    q: Optional[str] = Field(
        default=None,
        q=["localizacao__icontains", "edificacao__nome__icontains", "edificacao__codigo__icontains"],
        description="Campo de pesquisa por localizacão ou nome de edificação"
    ) # type: ignore
    edificacao__campus: Optional[str] = Field(
        default=None,
        alias="campus"
    )
    tipo: List[int] = Field(
        default=[0, 1, 2, 3, 4, 5, 6],
        alias="tipo",
        q=["tipo__in"],
    ) # type: ignore
    # status: Optional[bool] = Field(default=None)


PontoColetaIn.model_rebuild()
PontoColetaOut.model_rebuild()
