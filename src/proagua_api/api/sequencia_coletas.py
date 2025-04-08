from typing import List
import time

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Subquery, OuterRef
from ninja import Router, Query
from ninja.errors import HttpError

from proagua_api.api.exceptions.invalid_reference import InvalidReferenceException

from .pagination.pagination import paginate
from .pagination.custom_paginator import CustomPaginator
from .. import models
from .schemas.sequencia_coletas import *
from .schemas import ResponseSchema, PaginatedResponseSchema
from .utils import response
from ..services import sequencia_coletas as service_sequencia_coleta

router = Router(tags=["Sequencias"])


@router.get("", response=PaginatedResponseSchema[SequenciaColetasOut])
@paginate(CustomPaginator)
def list_sequencia(request, filter: Query[FilterSequenciaColetas]):
    parametros = models.ParametrosReferencia.objects.first()

    # Consolidar select_related e prefetch_related
    qs = models.SequenciaColetas.objects.select_related(
        'ponto', 'ponto__edificacao', 'ponto__amontante'
    ).prefetch_related(
        'coletas', 'ponto__imagens', 'ponto__edificacao__imagens', 'ponto__amontante__imagens'
    )

    # Uma única subquery para obter todas as coletas
    ultima_coleta = models.Coleta.objects.filter(sequencia=OuterRef('pk')).order_by('-data')[:1]

    # Usar annotate para coletar dados da ultima coleta da sequencia
    qs = qs.annotate(
            quantidade_coletas=Count('coletas'),
            ultima_coleta_turbidez=Subquery(ultima_coleta.values('turbidez')),
            ultima_coleta_cloro=Subquery(ultima_coleta.values('cloro_residual_livre')),
            ultima_coleta_escherichia=Subquery(ultima_coleta.values('escherichia')),
            ultima_coleta_coliformes=Subquery(ultima_coleta.values('coliformes_totais')),
            ultima_coleta=Subquery(ultima_coleta.values('data')),
        )

    # Filtrar sequências de coletas
    if filter.q:
        qs = qs.filter(
            Q(ponto__localizacao__icontains=filter.q) | 
            Q(ponto__edificacao__nome__icontains=filter.q) | 
            Q(ponto__edificacao__codigo__icontains=filter.q)
        )
    
    if filter.ponto__edificacao__campus:
        qs = qs.filter(ponto__edificacao__campus=filter.ponto__edificacao__campus)

    if filter.amostragem:
        qs = qs.filter(amostragem=filter.amostragem)
    
    qs = filter.filter(qs)

    # Retornar resultado
    qs = service_sequencia_coleta.set_status(qs, parametros)
    qs = service_sequencia_coleta.write_message(qs, parametros)
    
    return qs


@router.get("/{id_sequencia}", response=ResponseSchema[SequenciaColetasOut])
def get_sequencia(request, id_sequencia: int):
    qs = get_object_or_404(models.SequenciaColetas, id=id_sequencia)
    return response(data=qs)


@router.post("", response=ResponseSchema[SequenciaColetasOut])
def create_sequencia(request, payload: SequenciaColetasIn):
    ponto = get_object_or_404(models.PontoColeta, id=payload.ponto_id)

    payload_dict = payload.dict()
    payload_dict.pop('ponto_id')
    payload_dict["ponto"] = ponto

    sequencia = models.SequenciaColetas.objects.create(**payload_dict)
    sequencia.save()

    return response(data=sequencia)


@router.put("/{id_sequencia}", response=ResponseSchema[SequenciaColetasOut])
def update_sequencia(request, id_sequencia: int, payload: SequenciaColetasIn):
    sequencia = get_object_or_404(models.SequenciaColetas, id=id_sequencia)
    ponto = models.PontoColeta.objects.filter(pk=payload.ponto_id).first()

    # Check if the ponto exists
    if ponto is None:
        raise InvalidReferenceException(
            ref_name='Ponto',
            ref_id=payload.ponto_id, 
            field='ponto'
        )

    # Put the ponto object inside the payload data dictionary
    data = payload.dict()
    data["ponto"] = ponto

    # Change the sequencia values and save
    for attr, value in data.items():
        setattr(sequencia, attr, value)
    sequencia.save()
    
    return response(data=sequencia)


@router.delete("/{id_sequencia}", response=ResponseSchema)
def delete_sequencia(request, id_sequencia: int):
    sequencia = get_object_or_404(models.SequenciaColetas, id=id_sequencia)
    if models.SequenciaColetas.has_dependent_objects(sequencia):
        raise HttpError(409, "Conflict: Related objects exist")
    sequencia.delete()
    return response(data={'id': id_sequencia})


@router.get("/{id_sequencia}/coletas", response=PaginatedResponseSchema[ColetaOut])
def list_coletas_sequencia(request, id_sequencia: int):
    qs = models.Coleta.objects.filter(sequencia__id=id_sequencia)
    return response(
        data={
            "items": qs,
            "count": qs.count()
        }
    )


@router.get("/{id_sequencia}/pontos", response=PaginatedResponseSchema[PontoColetaOut])
def list_pontos_sequencia(request, id_sequencia: int):
    sequencia = get_object_or_404(models.SequenciaColetas, pk=id_sequencia)
    pontos: list[models.PontoColeta] = []
    
    ponto = sequencia.ponto
    while ponto is not None:
        pontos.append(ponto)
        ponto = ponto.amontante
    
    return response(
        data={
            "items": pontos,
            "count": len(pontos)
        }
    )
