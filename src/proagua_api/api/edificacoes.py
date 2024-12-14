from typing import List, Dict
import uuid

from django.shortcuts import get_object_or_404
from ninja import Router, Query, UploadedFile, File, Form
from ninja.errors import HttpError
from ninja.pagination import paginate

from .schemas.edficacao import *
from .schemas.ponto_coleta import (PontoColetaIn, PontoColetaOut)
from .. import models
from .utils import save_file

router = Router(tags=["Edificacoes"])

@router.get("", response=List[EdificacaoOut])
@paginate
def list_edificacoes(request, filters: FilterEdificacao = Query(...)):
    qs = models.Edificacao.objects.all()
    return filters.filter(qs)


@router.get("/{cod_edificacao}", response=EdificacaoOut)
def get_edificacao(request, cod_edificacao: str):
    qs = get_object_or_404(models.Edificacao, codigo=cod_edificacao)
    return qs


@router.post("/{cod_edificacao}/imagem")
def upload_image(request, cod_edificacao: str, description: str = Form(...), file: UploadedFile = File(...)):
    edificacao = get_object_or_404(models.Edificacao, codigo=cod_edificacao)
    
    img_path = save_file(f'media/images/edificacoes/edificacao_{edificacao.codigo}_{uuid.uuid4()}.png', file)
    image = models.Image.objects.create(src=img_path, description=description)
    image.save()

    edificacao.imagens.add(image)
    edificacao.save()
    
    return {"success": True}


@router.delete("/{cod_edificacao}/imagem/{id_imagem}")
def delete_image(request, cod_edificacao: str, id_imagem: uuid.UUID):
    edificacao = get_object_or_404(models.Edificacao, codigo=cod_edificacao)
    image: models.Image = edificacao.imagens.filter(id=id_imagem).first()

    if image is None:
        return HttpError(404, "Not found")
    
    image.src.delete()
    image.delete()
    return {"success": True}


@router.post("", response=EdificacaoOut)
def create_edificacao(request, payload: EdificacaoIn):
    data = payload.dict()
    edificacao = models.Edificacao.objects.create(**data)
    edificacao.save()
    
    return edificacao


@router.put("/{cod_edificacao}")
def update_edificacoes(request, cod_edificacao: str, payload: EdificacaoIn):
    edificacao = get_object_or_404(models.Edificacao, codigo=cod_edificacao)
    for attr, value in payload.dict().items():
        setattr(edificacao, attr, value)
    edificacao.save()
    return {"success": True}


@router.delete("/{cod_edificacao}")
def delete_edificacao(request, cod_edificacao: str):
    edificacao = get_object_or_404(models.Edificacao, codigo=cod_edificacao)

    if models.Edificacao.has_dependent_objects(edificacao):
        raise HttpError(409, "Conflict: Related objects exist")

    edificacao.delete()
    return {"success": True}


@router.get("/{cod_edificacao}/pontos")
def list_pontos(request, cod_edificacao: str):
    qs = models.PontoColeta.objects.filter(edificacao__codigo=cod_edificacao).values()
    return {"items": list(qs)}
