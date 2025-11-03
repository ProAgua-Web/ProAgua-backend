from enum import Enum

from django.db import models

from .image import Image


class Status(Enum):
    PENDENTE = "Pendente"
    EM_ANDAMENTO = "Em andamento"
    CONCLUIDO = "Concluido"


class TipoSolicitacao(Enum):
    LIMPEZA_RESERVATORIO = "Limpeza de reservatório"
    INSTALACAO_PONTO = "Instalação de ponto de coleta"
    CONSERTO_RESERVATORIO = "Conserto de reservatório"
    OUTRO = "Outro"


class Solicitacao(models.Model):
    ponto = models.ForeignKey(
        to="PontoColeta",
        related_name="Solicitacao",
        verbose_name="ponto de coleta",
        on_delete=models.PROTECT,
        blank=False
    )
    data = models.DateTimeField(
        verbose_name="data da solicitação",
        auto_now_add=True
    )

    objetivo = models.TextField(
        verbose_name="objetivo da solicitação",
        max_length=1250,
        blank=True,
        null=True
    )
    justificativa = models.TextField(
        verbose_name="justificativa da solicitação",
        max_length=1250,
        blank=True,
        null=True
    )

    tipo = models.CharField(
        verbose_name="tipo de solicitação",
        max_length=50,
        choices=[(tag.value, tag.value) for tag in TipoSolicitacao],
        default=TipoSolicitacao.LIMPEZA_RESERVATORIO.value
    )

    status = models.CharField(
        verbose_name="status",
        max_length=50,
        choices=[(tag.value, tag.value) for tag in Status],
        default=Status.PENDENTE
    )

    imagens = models.ManyToManyField(to=Image)
