from typing import Any

from ninja.pagination import PaginationBase
from ninja import Schema

from ..schemas import PaginatedResponseSchema


class CustomPaginator(PaginationBase):
    class Input(Schema):
        limit: int = 100
        offset: int = 0

    Output = PaginatedResponseSchema[Any]

    def paginate_queryset(self, queryset, pagination: Input, **params):
        queryset = list(queryset)
        count = len(queryset)
        
        if pagination.limit > 0:
            items = queryset[pagination.offset: pagination.offset + pagination.limit]
        else:
            items = queryset[pagination.offset:]
        
        return  {
            "data": {
                "items": items,
                "count": count,
            }
        }
