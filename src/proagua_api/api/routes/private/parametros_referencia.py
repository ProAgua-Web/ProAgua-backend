"""
Material de referência:
    https://django-ninja.rest-framework.com/tutorial/other/crud/
    https://django-ninja.rest-framework.com/guides/response/?h=resolvers#resolvers
"""

from ninja import Router

from .... import models
from ...schemas.parametros_referencia import ParametrosReferenciaIn, ParametrosReferenciaOut

router = Router(tags=["ParametrosReferencia"])

@router.get("", response=ParametrosReferenciaOut)
def get_parametros_referencia(request):
    qs = models.ParametrosReferencia.objects.all()
    if qs.exists():
        return qs.last()
    return {"success": False}


@router.post("", response=ParametrosReferenciaOut)
def create_parametros_referencia(request, payload: ParametrosReferenciaIn):
    qs = models.ParametrosReferencia.objects.all()
    if not qs.exists():
        obj_parametros_referencia = models.ParametrosReferencia.objects.create(**payload.dict())
        return obj_parametros_referencia
    return {"success": False}

@router.put("", response=ParametrosReferenciaOut)
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

    return obj_parametros_referencia

@router.delete("")
def delete_parametros_referencia(request):
    qs = models.ParametrosReferencia.objects.all()
    if qs.exists():
        qs.delete()
        return {"success": True}
    return {"success": False}