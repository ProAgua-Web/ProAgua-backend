"""
Material de referência:
    https://django-ninja.rest-framework.com/tutorial/other/crud/
    https://django-ninja.rest-framework.com/guides/response/?h=resolvers#resolvers
"""

from ninja import Router
from django.shortcuts import get_object_or_404

from .... import models
from ...utils import save_file, response
from ...schemas import ResponseSchema
from ...schemas.parametros_referencia import ParametrosReferenciaIn, ParametrosReferenciaOut

router = Router(tags=["ParametrosReferencia"])

@router.get("", response=ResponseSchema[ParametrosReferenciaOut])
def get_parametros_referencia(request):
    parametros = get_object_or_404(models.ParametrosReferencia, id=1)
    return response(data=parametros)


@router.post("", response=ResponseSchema[ParametrosReferenciaOut|dict])
def create_parametros_referencia(request, payload: ParametrosReferenciaIn):
    qs = models.ParametrosReferencia.objects.all()
    if not qs.exists():
        obj_parametros_referencia = models.ParametrosReferencia.objects.create(**payload.dict())
        return response(data=obj_parametros_referencia)
    return response(data={'success': False})


@router.put("", response=ResponseSchema[ParametrosReferenciaOut])
def update_parametros_referencia(request, payload: ParametrosReferenciaIn):
    obj_parametros_referencia = models.ParametrosReferencia.objects.last()
    data_dict = payload.dict()

    for attr, value in data_dict.items():
        setattr(obj_parametros_referencia, attr, value)

    obj_parametros_referencia.save()

    coletas = models.Coleta.objects.all()
    for coleta in coletas:
        coleta.analise()
        coleta.save()

    return response(data=obj_parametros_referencia)

@router.delete("", response=ResponseSchema)
def delete_parametros_referencia(request):
    qs = models.ParametrosReferencia.objects.all()
    if qs.exists():
        qs.delete()
        return response(data={"success": True})
    return response(data={"success": False})