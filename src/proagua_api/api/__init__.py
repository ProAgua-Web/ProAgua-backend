import re

from ninja import NinjaAPI
from django.http import JsonResponse, Http404
from django.middleware.csrf import get_token
from ninja.errors import ValidationError
from ninja.errors import HttpError
from django.db.utils import IntegrityError

from proagua_api.api.exceptions.invalid_reference import InvalidReferenceException

from . import (
    auth,
    edificacoes,
    pontos,
    coletas,
    sequencia_coletas,
    usuarios,
    parametros_referencia,
    solicitacoes,
)

from .schemas import ResponseSchema
from .utils import response

api = NinjaAPI(auth=auth.JWTBearer(), csrf=False)


# Exception handlers
@api.exception_handler(ValidationError)
def validation_error_handler(request, exc: ValidationError):
    errors: list = []

    for e in exc.errors:
        errors.append({
            "type": "ValidationError",
            "message": e["msg"],
            "field": e["loc"][-1]
        })
    
    return api.create_response(
        request=request,
        data=response(errors=errors),
        status=400
    )


@api.exception_handler(IntegrityError)
def integrity_error_handler(request, exc: IntegrityError):
    errors: list = []
    error_message = str(exc)
    
    # Erro de chave única (valor duplicado)
    if "duplicate key value violates unique constraint" in error_message:
        match = re.search(r'unique constraint \"(.+?)\"', error_message)
        match_key = re.search(r'Key \((.+?)\)=\((.+?)\)', error_message)
        campo, valor = match_key.groups() if match_key else ("campo desconhecido", "valor já existente")
        error_message = f"O valor '{valor}' já existe no campo '{campo}'. Escolha um valor diferente!"

        # Tratamento extra para chave composta
        if ',' in campo:
            campos = campo.split(',')
            valores = valor.split(',')

            for c, v in zip(campos, valores):
                errors.append({
                    "type": "IntegrityError",
                    "message": f"O valor '{v}' já existe no campo '{c}'. Escolha um valor diferente!",
                    "field": c
                })

    # Erro de chave primária duplicada
    elif "UNIQUE constraint failed" in error_message:
        match = re.search(r'UNIQUE constraint failed: (.+?)\.', error_message)
        campo = match.group(1) if match else "um campo único"
        error_message = f"Já existe um registro com este valor em '{campo}'. Tente algo diferente!"

    # Erro de chave estrangeira
    elif "FOREIGN KEY constraint failed" in error_message:
        error_message = "Parece que está tentando referenciar algo que não existe! Verifique os dados antes de salvar."

    # Erro de campo obrigatório (`NOT NULL`)
    elif "NOT NULL constraint failed" in error_message:
        match = re.search(r'NOT NULL constraint failed: (.+?)\.', error_message)
        campo = match.group(1) if match else "um campo obrigatório"
        error_message = f"O campo '{campo}' é obrigatório! Certifique-se de preenchê-lo antes de continuar."

    else:
        error_message = "Ocorreu um erro."
    
    errors.append({
        "type": "IntegrityError",
        "message": error_message,
    })

    return api.create_response(
        request=request,
        data=response(errors=errors),
        status=400
    )


@api.exception_handler(HttpError)
def http_error_handler(request, exc: HttpError):
    errors = [
        {
            "type": f'Http{exc.status_code}',
            "message": exc.message
        }
    ]

    return api.create_response(
        request=request,
        data=response(errors=errors),
        status=exc.status_code
    )


@api.exception_handler(Exception)
def exception_handler(request, exc: Exception):
    errors = [
        {
            "type": "Exception",
            "message": "Ocorreu um erro no sistema" + str(exc)
        }
    ]

    return api.create_response(
        request=request,
        data=response(errors=errors),
        status=500
    )


@api.exception_handler(Http404)
def http_404_handler(request, exc: Exception):
    errors = [
        {
            "type": "Http404",
            "message": str(exc)
        }
    ]

    return api.create_response(
        request=request,
        data=response(errors=errors),
        status=404
    )


@api.exception_handler(InvalidReferenceException)
def invalid_reference_handler(request, exc: InvalidReferenceException):
    errors = [
        {
            "type": "InvalidReference",
            "message": str(exc),
            "field": exc.field
        }
    ]

    return api.create_response(
        request=request,
        data=response(errors=errors),
        status=404
    )


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
