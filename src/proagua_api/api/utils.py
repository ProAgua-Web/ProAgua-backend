import os
from io import BytesIO
from typing import List, Dict, Optional

from django.conf import settings
from ninja import UploadedFile, File
from PIL import Image


def response(
        data: Optional[Dict]=None,
        errors: Optional[List]=None,
    ):

    return {
        "data": data,
        "errors": errors,
    }


def save_file(file_path: str, file: File[UploadedFile]) -> str:
    file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    image = Image.open(BytesIO(file.read()))
    image.save(file_path)

    return os.path.relpath(file_path, settings.MEDIA_ROOT)
