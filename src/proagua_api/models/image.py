import uuid

from django.db import models


class Image(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    src = models.ImageField(
        upload_to="media/images",
    )
    description = models.TextField(
        verbose_name="Descrição",
        max_length=250
    )