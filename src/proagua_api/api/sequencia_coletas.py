from typing import List
import time

from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Subquery, OuterRef
from ninja import Router, Query
from ninja.pagination import paginate
from ninja.errors import HttpError

from .schemas.sequencia_coletas import *
from .. import models

router = Router(tags=["Sequencias"])


def write_message(qs, parametros):
    # Primeiro, busque todos os objetos no queryset sem o annotate
    qs = list(qs) 

    # Itera sobre cada item do queryset e cria as mensagens manualmente
    for item in qs:
        if item.ultima_coleta is not None:
            
            # Verifica e cria a mensagem de turbidez
            if item.ultima_coleta_turbidez > parametros.max_turbidez:
                item.mensagem_turbidez = f"Turbidez está {item.ultima_coleta_turbidez - parametros.max_turbidez} uT acima do limite máximo"
            elif item.ultima_coleta_turbidez < parametros.min_turbidez:
                item.mensagem_turbidez = f"Turbidez está {parametros.min_turbidez - item.ultima_coleta_turbidez} uT abaixo do limite mínimo"
            else:
                item.mensagem_turbidez = ""
            
            # Verifica e cria a mensagem de cloro
            if item.ultima_coleta_cloro > parametros.max_cloro_residual_livre:
                item.mensagem_cloro = f"Cloro está {item.ultima_coleta_cloro - parametros.max_cloro_residual_livre} acima do limite máximo"
            elif item.ultima_coleta_cloro < parametros.min_cloro_residual_livre:
                item.mensagem_cloro = f"Cloro está {parametros.min_cloro_residual_livre - item.ultima_coleta_cloro} abaixo do limite mínimo"
            else:
                item.mensagem_cloro = ""

            # Verifica e cria a mensagem para coliformes
            if item.ultima_coleta_coliformes:
                item.mensagem_coliformes = "Presença de coliformes"    
            else:
                item.mensagem_coliformes = ""

            # Verifica e cria a mensagem para escherichia coli
            if item.ultima_coleta_escherichia:
                item.mensagem_escherichia = "Presença de escherichia coli"
            else:
                item.mensagem_escherichia = ""
        else:
            item.mensagem_turbidez = ""
            item.mensagem_cloro = ""
            item.mensagem_coliformes = ""
            item.mensagem_escherichia = ""

        # Compondo a mensagem final de status
        if item.quantidade_coletas == 0:
            item.status_message = "Não há coletas registradas para esta sequência."
        elif (
            not item.status_turbidez
            or not item.status_cloro
            or item.ultima_coleta_escherichia
            or item.ultima_coleta_coliformes
        ):
            item.status_message = ". ".join(
                filter(None, [
                    item.mensagem_turbidez,
                    item.mensagem_cloro,
                    item.mensagem_coliformes,
                    item.mensagem_escherichia
                ])
            )
        else:
            item.status_message = "Todos os parâmetros estão dentro dos limites."
    
    return qs


def set_status(qs, parametros):
    # Primeiro, busque todos os objetos no queryset sem o annotate
    qs = list(qs)  # Converte o queryset para uma lista para processar individualmente.

    # Itera sobre cada item do queryset e define os campos de status manualmente
    for item in qs:
        item.status_turbidez = None
        item.status_cloro = None
    
        if item.ultima_coleta is not None:
            # Verifica o status de turbidez
            item.status_turbidez = parametros.min_turbidez <= item.ultima_coleta_turbidez <= parametros.max_turbidez

            # Verifica o status de cloro
            item.status_cloro = parametros.min_cloro_residual_livre <= item.ultima_coleta_cloro <= parametros.max_cloro_residual_livre

            # Verifica o status geral (True se todas as condições forem atendidas)
            item.status = (
                item.status_turbidez
                and item.status_cloro
                and not item.ultima_coleta_escherichia
                and not item.ultima_coleta_coliformes
            )
        else:
            item.status = None
    
    return qs

@router.get("", response=List[SequenciaColetasOut])
@paginate
def list_sequencia(request, filter: FilterSequenciaColetas = Query(...)):
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
    qs = set_status(qs, parametros)
    qs = write_message(qs, parametros)
    return qs


@router.get("/{id_sequencia}", response=SequenciaColetasOut)
def get_sequencia(request, id_sequencia: int):
    qs = get_object_or_404(models.SequenciaColetas, id=id_sequencia)
    return qs


@router.post("")
def create_sequencia(request, payload: SequenciaColetasIn):
    id_ponto = payload.dict().get("ponto")
    ponto = get_object_or_404(models.PontoColeta, id=id_ponto)

    payload_dict = payload.dict()
    payload_dict["ponto"] = ponto

    sequencia = models.SequenciaColetas.objects.create(**payload_dict)
    sequencia.save()
    return {"success": True}


@router.put("/{id_sequencia}")
def update_sequencia(request, id_sequencia: int, payload: SequenciaColetasIn):
    sequencia = get_object_or_404(models.SequenciaColetas, id=id_sequencia)
    for attr, value in payload.dict().items():
        setattr(sequencia, attr, value)
    sequencia.save()
    return {"success": True}


@router.delete("/{id_sequencia}")
def delete_sequencia(request, id_sequencia: int):
    sequencia = get_object_or_404(models.SequenciaColetas, id=id_sequencia)
    
    if models.SequenciaColetas.has_dependent_objects(sequencia):
        raise HttpError(409, "Conflict: Related objects exist")

    sequencia.delete()
    return {"success": True}


@router.get("/{id_sequencia}/coletas", response=List[ColetaOut])
def list_coletas_sequencia(request, id_sequencia: int):
    qs = models.Coleta.objects.filter(sequencia__id=id_sequencia)
    return qs
