import re

from ninja import NinjaAPI
from django.http import JsonResponse, Http404
from django.middleware.csrf import get_token
from ninja.errors import ValidationError
from ninja.errors import HttpError
from django.db.utils import IntegrityError

from .exceptions.invalid_reference import InvalidReferenceException
from .exceptions.generic_exception import GenericException
from .utils import response
from .routes.private import private_router
from .routes.public import public_router

api = NinjaAPI()

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
    field = None

    # Erro de chave única (valor duplicado)
    if "duplicate key value violates unique constraint" in error_message:
        match = re.search(r'unique constraint \"(.+?)\"', error_message)
        match_key = re.search(r'Key \((.+?)\)=\((.+?)\)', error_message)
        field, value = match_key.groups() if match_key else ("campo desconhecido", "valor já existente")
        error_message = f"O valor '{value}' já existe no campo '{field}'. Escolha um valor diferente!"

        # Tratamento extra para chave composta
        if ',' in field:
            campos = field.split(',')
            valores = value.split(',')

            for field, value in zip(campos, valores):
                field = field.lstrip().rstrip()
                errors.append({
                    "type": "IntegrityError",
                    "message": f"O valor '{value}' já existe no campo '{field}'. Escolha um valor diferente!",
                    "field": field
                })

    # Erro de chave primária duplicada
    elif "UNIQUE constraint failed" in error_message:
        match = re.search(r'UNIQUE constraint failed: (.+?)\.', error_message)
        field = match.group(1) if match else "um campo único"
        error_message = f"Já existe um registro com este valor em '{field}'. Tente algo diferente!"
        
    
    # Erro de chave estrangeira
    elif "FOREIGN KEY constraint failed" in error_message:
        error_message = "Parece que está tentando referenciar algo que não existe! Verifique os dados antes de salvar."

    # Erro de campo obrigatório (`NOT NULL`)
    elif "null value in column" in error_message:
        match = re.search(r'null value in column "(.+)" of relation', error_message)
        field = match.group(1) if match else "UNKNOW_FIELD"
        error_message = f"O campo '{field}' é obrigatório! Certifique-se de preenchê-lo antes de continuar."
    else:
        error_message = "Ocorreu um erro."
        
    errors.append({
        "type": "IntegrityError",
        "message": error_message,
        "field": field
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


@api.exception_handler(GenericException)
def generic_exception_handler(request, exc: GenericException):
    errors = [
        {
            "type": exc.type,
            "message":  exc.message,
            "field": exc.field,
        }
    ]

    return api.create_response(
        request=request,
        data=response(errors=errors),
        status=500
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


@api.get("/csrf", auth=None)
def get_csrf_token(request):
    token = get_token(request)
    response = JsonResponse({"csrftoken": token})
    response.set_cookie('csrftoken', token, path='/', samesite='None', secure=True)
    return response


api.add_router('', private_router)
api.add_router('/public', public_router)
