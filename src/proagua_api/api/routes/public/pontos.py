from ninja import Router
from django.shortcuts import get_object_or_404
from ninja import Query

from ...schemas import ResponseSchema, PaginatedResponseSchema
from ...schemas.edficacao import *
from ...schemas.ponto_coleta import PontoColetaOut, FilterPontos
from ...schemas.coleta import ColetaOut

from .... import models
from ...utils import response
from ...pagination.pagination import paginate
from ...pagination.custom_paginator import CustomPaginator

router = Router(tags=["Pontos"])


@router.get("", response=PaginatedResponseSchema[PontoColetaOut])
@paginate(CustomPaginator)
def list_ponto(request, filters: Query[FilterPontos]):
    """Endpoint público para listagem de pontos"""

    qs = models.PontoColeta.objects
    qs = qs.select_related("edificacao")
    qs = qs.prefetch_related("imagens", "edificacao__imagens")
    qs = filters.filter(qs)
    
    return qs.all()


@router.get("/{id_ponto}", response=ResponseSchema[PontoColetaOut])
def get_ponto(request, id_ponto: int):
    """ Endpoint publico para busca de um ponto"""
    qs = get_object_or_404(models.PontoColeta, id=id_ponto)
    return response(data=qs) # type: ignore


@router.get("/{id_ponto}/coleta", response=ResponseSchema[ColetaOut])
def get_coleta(request, id_ponto: int):
    """Endpoins público que retorna a última coleta pública realizada no ponto"""
    coleta = get_object_or_404(models.Coleta, ponto_id=id_ponto, publico=True)
    return response(data=coleta) # type: ignore
