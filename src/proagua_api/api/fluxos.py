from typing import List

from ninja import Router
from ninja.pagination import paginate
from django.shortcuts import get_object_or_404

from .schemas.fluxo import FluxoOut, FluxoIn
from proagua_api.models.fluxo import Fluxo

router = Router()


@router.get("", response=List[FluxoOut], tags=["Fluxos"])
@paginate
def list_fluxo(request):
    qs = Fluxo.objects.all()
    return qs


@router.get("/{id_fluxo}", response=FluxoOut, tags=["Fluxos"])
def get_fluxo(request, id_fluxo: int):
    fluxo = get_object_or_404(Fluxo, id=id_fluxo)
    return fluxo


@router.post("", response=FluxoOut, tags=["Fluxos"])
def create_fluxo(request, data: FluxoIn):
    fluxo = Fluxo.objects.create()
    fluxo.pontos.set(data.pontos)
    fluxo.save()
    return fluxo


@router.put("/{id_fluxo}", tags=["Fluxos"])
def update_fluxo(request, id_fluxo: int, data: FluxoIn):
    fluxo = get_object_or_404(Fluxo, id=id_fluxo)
    fluxo.pontos.set(data.pontos)
    fluxo.save()
    return {"status": "success"}


@router.delete("/{id_fluxo}", tags=["Fluxos"])
def delete_fluxo(request, id_fluxo: int):
    fluxo = get_object_or_404(Fluxo, id=id_fluxo)
    fluxo.delete()
    return {"status": "success"}
