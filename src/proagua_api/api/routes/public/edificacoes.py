from django.shortcuts import get_object_or_404
from ninja import Router, Query

from ...schemas import ResponseSchema, PaginatedResponseSchema
from ...schemas.edficacao import *
from .... import models
from ...utils import response
from ...pagination.pagination import paginate
from ...pagination.custom_paginator import CustomPaginator

router = Router(tags=["Edificacoes"])

@router.get("", response=PaginatedResponseSchema[EdificacaoOut])
@paginate(CustomPaginator)
def list_edificacoes(request, filters: Query[FilterEdificacao]):
    """Endpoint público para listar todas as edificações"""
    qs = models.Edificacao.objects.all()
    qs = filters.filter(qs)
    return qs


@router.get("/{cod_edificacao}", response=ResponseSchema[EdificacaoOut])
def get_edificacao(request, cod_edificacao: str):
    """Endpoint público para buscar edificação"""
    qs = get_object_or_404(models.Edificacao, codigo=cod_edificacao)
    return response(data=qs) # type: ignore

