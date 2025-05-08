from ninja import Router
from . import (
    edificacoes,
    pontos
)

public_router = Router()

public_router.add_router('/edificacoes', edificacoes.router)
public_router.add_router('/pontos', pontos.router)
