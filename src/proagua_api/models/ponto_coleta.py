from django.db import models
from .coleta import Coleta
from .image import Image

TIPOS_PONTOS = (
    (0, "Bebedouro"),
    (1, "Torneira"),
    (2, "Reservatório predial superior"),
    (3, "Reservatório predial inferior"),
    (4, "Reservatório de distribuição superior"),
    (5, "Reservatório de distribuição inferior"),
    (6, "CAERN")
)


class PontoColeta(models.Model):
    # Caracteristicas gerais de um ponto de coleta
    id = models.AutoField(primary_key=True)

    imagens = models.ManyToManyField(to=Image, blank=True)

    edificacao = models.ForeignKey(
        to="Edificacao",
        related_name="PontoColeta",
        verbose_name="código da edificação",
        on_delete=models.PROTECT,
        blank=False
    )

    tipo = models.IntegerField(
        verbose_name="tipo",
        choices=TIPOS_PONTOS,
        default=TIPOS_PONTOS[0] # type: ignore
    )

    amontante = models.ForeignKey(
        to="PontoColeta",
        verbose_name="ponto amontante",
        related_name="ponto_amontante",
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    localizacao = models.CharField(
        verbose_name="localizacao",
        max_length=255,
        blank=True,
        null=True
    )

    observacao = models.TextField(
        verbose_name="observação",
        blank=True,
        null=True
    )

    # Parâmetros de exclusivo de bebedouro

    tombo = models.CharField(
        max_length=40,
        verbose_name="tombo",
        blank=True,
        null=True
    )

    # Reservatorio
    quantidade = models.IntegerField(
        verbose_name="quantidade",  # unico, duplo, triplo
        blank=True,
        null=True
    )

    capacidade = models.FloatField(
        verbose_name="capacidade em (L)",
        blank=True,
        null=True
    )

    material = models.CharField(
        verbose_name="material",
        max_length=255,
        blank=True,
        null=True
    )

    fonte_informacao = models.CharField(
        verbose_name="fonte de informação",
        max_length=255,
        blank=True,
        null=True
    )

    def status(self) -> bool | None:
        coleta = Coleta.objects.filter(ponto=self).last()
        if coleta:
            return coleta.status

    def status_message(self) -> str | None:
        coleta = Coleta.objects.filter(ponto=self).last()
        if coleta:
            return coleta.status_message

    def has_dependent_objects(instance):
        for related_object in instance._meta.related_objects:
            related_name = related_object.get_accessor_name()
            related_manager = getattr(instance, related_name)
            if related_manager.exists():
                return True
        return False

    def __str__(self) -> str:
        return f"Ponto {self.id} - {self.get_tipo_display()}"
