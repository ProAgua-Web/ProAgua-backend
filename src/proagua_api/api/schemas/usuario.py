from django.contrib.auth.models import User
from ninja import ModelSchema


class UsuarioIn(ModelSchema):
    class Config: # type: ignore
        model = User
        model_fields = [
            "username",
            "first_name",
            "last_name",
            "password",
            "email",
            "is_superuser"
        ]

class UsuarioUpdate(ModelSchema):
    class Config: # type: ignore
        model = User
        model_fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_superuser"
        ]


class UsuarioOut(ModelSchema):
    class Config: # type: ignore
        model = User
        model_exclude = ["password", "user_permissions", "last_login"]
