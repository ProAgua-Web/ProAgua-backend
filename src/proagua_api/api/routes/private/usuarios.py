from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja import Router

from ...pagination.pagination import paginate
from ...pagination.custom_paginator import CustomPaginator
from ...schemas import ResponseSchema, PaginatedResponseSchema
from ...schemas.usuario import UsuarioOut, UsuarioIn, UsuarioUpdate
from ...utils import response

router = Router(tags=["Usuarios"])


@router.get("", response=PaginatedResponseSchema[UsuarioOut])
@paginate(CustomPaginator)
def list_usuario(request):
    qs = User.objects.all()
    return qs


@router.get("/{username}", response=ResponseSchema[UsuarioOut])
def get_usuario(request, username: str):
    user = get_object_or_404(User, username=username)
    return response(data=user)


@router.post("",  response=ResponseSchema[UsuarioOut])
def create_usuario(request, payload: UsuarioIn):
    user_data = payload.dict()
    user = User.objects.create_user(**user_data)
    user.save()
    return response(data=user)


@router.put("/{username}", response=ResponseSchema[UsuarioOut])
def update_usuario(request, username: str, payload: UsuarioUpdate):
    user = get_object_or_404(User, username=username)
    for attr, value in payload.dict().items():
        setattr(user, attr, value)
    user.save()
    return response(data=user)


@router.delete("/{username}", response=ResponseSchema[UsuarioOut])
def delete_usuario(request, username: str):
    user = get_object_or_404(User, username=username)
    user.delete()
    return response(data={'id': user.pk})
