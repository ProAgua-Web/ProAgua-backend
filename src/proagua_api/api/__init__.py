from ninja import NinjaAPI
from django.http import JsonResponse
from django.middleware.csrf import get_token

from . import (
    auth,
    edificacoes,
    pontos,
    coletas,
    sequencia_coletas,
    usuarios,
    parametros_referencia,
    solicitacoes
)

from .schemas import ResponseSchema

api = NinjaAPI(auth=auth.JWTBearer(), csrf=False)

# Public routes
@api.get("/csrf", auth=None)
def get_csrf_token(request):
    token = get_token(request)
    response = JsonResponse({"csrftoken": token})
    response.set_cookie('csrftoken', token, path='/', samesite='None', secure=True)
    return response


# Private routes
api.add_router("/auth", auth.router)
api.add_router("/edificacoes", edificacoes.router)
api.add_router("/pontos", pontos.router)
api.add_router("/sequencias", sequencia_coletas.router)
api.add_router("/coletas", coletas.router)
api.add_router("/parametros_referencia", parametros_referencia.router)
api.add_router("/usuarios", usuarios.router)
api.add_router("/solicitacoes", solicitacoes.router)
