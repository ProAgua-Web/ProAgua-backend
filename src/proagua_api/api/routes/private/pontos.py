"""
Material de referência:
    https://django-ninja.rest-framework.com/tutorial/other/crud/
    https://django-ninja.rest-framework.com/guides/response/?h=resolvers#resolvers
"""

from typing import List
import uuid

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router, Query, UploadedFile, File, Form
from ninja.errors import HttpError

from ...pagination.pagination import paginate
from ...pagination.custom_paginator import CustomPaginator
from ...schemas.ponto_coleta import *
from ...schemas.coleta import ColetaOut
from ...schemas import PaginatedResponseSchema, ResponseSchema
from ...utils import save_file, response
from .... import models

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
    return response(data=qs)


@router.get("/{id_ponto}/coleta", response=ResponseSchema[ColetaOut])
def get_coleta(request, id_ponto: int):
    """Endpoins público que retorna a última coleta pública realizada no ponto"""
    coleta = get_object_or_404(models.Coleta, ponto_id=id_ponto, publico=True)
    return response(data=coleta) # type: ignore


@router.post("/{id_ponto}/imagem", response=ResponseSchema[PontoColetaOut])
def upload_image(request, id_ponto: str, description: Form[str], file: File[UploadedFile]):
    ponto = get_object_or_404(models.PontoColeta, id=id_ponto)

    img_path = save_file(f'media/images/pontos/ponto_{ponto.id}_{uuid.uuid4()}.png', file)
    image = models.Image.objects.create(src=img_path, description=description)
    image.save()

    ponto.imagens.add(image)
    ponto.save()
    
    return response(data=ponto)


@router.delete('/{id_ponto}/imagem/{id_imagem}')
def delete_image(request, id_ponto: str, id_imagem: uuid.UUID):
    ponto = get_object_or_404(models.PontoColeta, id=id_ponto)
    image: models.Image = ponto.imagens.filter(id=id_imagem).first()
    
    if image is None:
        return HttpError(404, "Not found")
    
    image.src.delete()
    image.delete()
    return {"success": True}


@router.post("", response=ResponseSchema[PontoColetaOut])
def create_ponto(request, payload: PontoColetaIn):
    edificacao = get_object_or_404(models.Edificacao, codigo=payload.codigo_edificacao)
    amontante = get_object_or_404(models.PontoColeta, id=payload.amontante_id) if payload.amontante_id else None    
    
    data_dict = payload.dict()
    data_dict.pop("codigo_edificacao")
    data_dict["edificacao"] = edificacao
    data_dict["amontante"] = amontante
    
    ponto_coleta = models.PontoColeta.objects.create(**data_dict)
    ponto_coleta.save()

    return response(data=ponto_coleta)


@router.put("/{id_ponto}", response=ResponseSchema[PontoColetaOut])
def update_ponto(request, id_ponto: int, payload: PontoColetaIn):
    ponto = get_object_or_404(models.PontoColeta, id=id_ponto)

    amontante = None
    if payload.amontante is not None:
        amontante = get_object_or_404(models.PontoColeta, id=payload.amontante)

    edificacao = get_object_or_404(models.Edificacao, codigo=payload.codigo_edificacao)

    data_dict = payload.dict()
    data_dict.pop("codigo_edificacao")
    data_dict["edificacao"] = edificacao
    data_dict["amontante"] = amontante

    for key, value in data_dict.items():
        setattr(ponto, key, value)

    ponto.save()

    return response(data=ponto)


@router.delete("/{id_ponto}", response=ResponseSchema)
def delete_ponto(request, id_ponto: int):
    ponto = get_object_or_404(models.PontoColeta, id=id_ponto)

    if models.PontoColeta.has_dependent_objects(ponto):
        raise HttpError(409, "Conflict: Related objects exist")
    
    ponto.delete()
    return response(data={'id': id_ponto})

    """Retorna todas as coletas associadas a um ponto de coleta"""
    qs = models.Coleta.objects.filter(ponto__id=id_ponto)
    items = list(qs)

    return response(
        data={
            "items": items,
            "count": len(items)
        }
    )