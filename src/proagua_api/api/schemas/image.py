from typing import Optional
from uuid import UUID

from ninja import Schema

class ImageOut(Schema):
    id: UUID
    src: str
    description: Optional[str] = None

class ImageIn(Schema):
    file: str
    description: Optional[str] = None

