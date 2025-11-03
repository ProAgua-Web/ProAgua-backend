from typing import Optional, Any

class InvalidReferenceException(ValueError):
    field: Optional[str]

    def __init__(self, ref_name, ref_id, message=None, field=None):
        self.ref_name = ref_name
        self.ref_id = ref_id
        self.field = field

        if message is None:
            message = f'Não foi possível encontrar o item {ref_name} com ID = {ref_id}.'

        super().__init__(message)