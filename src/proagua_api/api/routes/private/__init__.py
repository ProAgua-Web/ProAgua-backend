from ninja import Router

from . import(
    auth,
    edificacoes,
    pontos,
    sequencia_coletas,
    coletas,
    parametros_referencia,
    usuarios,
    solicitacoes,
)

private_router = Router(auth=auth.JWTBearer())

private_router.add_router("/auth", auth.router)
private_router.add_router("/edificacoes", edificacoes.router)
private_router.add_router("/pontos", pontos.router)
private_router.add_router("/sequencias", sequencia_coletas.router)
private_router.add_router("/coletas", coletas.router)
private_router.add_router("/parametros_referencia", parametros_referencia.router)
private_router.add_router("/usuarios", usuarios.router)
private_router.add_router("/solicitacoes", solicitacoes.router)
