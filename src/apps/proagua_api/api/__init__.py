from ninja import NinjaAPI
from ninja.security import django_auth

from . import edificacoes, pontos, coletas

api = NinjaAPI(auth=django_auth, csrf=True)

api.add_router("/edificacoes", edificacoes.router)
api.add_router("/pontos", pontos.router)
api.add_router("/coletas", coletas.router)