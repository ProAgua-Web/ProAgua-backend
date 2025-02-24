from ninja import Schema
from typing import Optional, List, Generic, TypeVar

T = TypeVar('T')


class ErrorSchema(Schema):
    type: str
    message: str
    field: Optional[str] = None


class ResponseSchema(Schema, Generic[T]):
    data: Optional[T] = None
    errors: Optional[List[ErrorSchema]] = None


class PaginatedObject(Schema, Generic[T]):
    items: List[T] = []
    count: int


class PaginatedResponseSchema(Schema, Generic[T]):
    data: PaginatedObject[T]
    errors: Optional[List[ErrorSchema]] = None
