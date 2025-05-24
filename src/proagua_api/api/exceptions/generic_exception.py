from typing import Optional


class GenericException(Exception):
    type: str
    message: str
    field: Optional[str]

    def __init__(self, err_type: str, message: str, field: Optional[str]=None):
        super().__init__(message)
        self.type = err_type
        self.message = message
        self.field = field
