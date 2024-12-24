from django.db import models
from django.contrib.auth.models import User

import csv
from io import StringIO

from .parametros_referencia import ParametrosReferencia

BEBEDOURO = 1
RPS = 2
RPI = 3
RDS = 4
RDI = 5
CAERN = 6

# TODO: Pensar em uma melhor forma de armazenar os status de coletas e pontos de coletas


class Coleta(models.Model):
    id = models.AutoField(primary_key=True)
    sequencia = models.ForeignKey(
        to="SequenciaColetas",
        verbose_name="sequência de Coletas",
        related_name="coletas",
        on_delete=models.PROTECT,
        blank=False,
        null=False
    )
    ponto = models.ForeignKey(
        to="PontoColeta",
        verbose_name="Ponto de Coleta",
        on_delete=models.PROTECT,
        related_name="coletas",
        blank=False,
        null=False
    )
    temperatura = models.FloatField(
        verbose_name="temperatura",
    )
    cloro_residual_livre = models.FloatField(
        verbose_name="cloro residual livre",
    )
    turbidez = models.FloatField(
        verbose_name="turbidez",
    )
    coliformes_totais = models.BooleanField(
        verbose_name="coliformes totais",
    )
    escherichia = models.BooleanField(
        verbose_name="escherichia coli",
    )
    cor = models.FloatField(
        verbose_name="cor"
    )
    data = models.DateTimeField(
        verbose_name="data da coleta",
    )
    responsavel = models.ManyToManyField(
        to=User,
        verbose_name="responsaveis",
        blank=True,
    )
    ordem = models.CharField(
        max_length=8,
        choices=(
            ("C", "Coleta"),
            ("R", "Recoleta")
        ),
        default=("C", "Coleta"),
    )
    status = models.BooleanField(
        verbose_name="status",
        default=None,
        null=True,
    )

    status_message = models.CharField(
        verbose_name="status message",
        max_length=200,
        default=None,
        null=True
    )

    def analise(self):
        status_temperatura = self.analise_temperatura()
        status_cloro_residual_livre = self.analise_cloro_residual_livre()
        status_turbidez = self.analise_turbidez()
        status_coliformes = self.analise_coliformes()
        status_escherichia = self.analise_escherichia()

        status = {
            "status": True,
            "messages": []
        }

        if not status_cloro_residual_livre["status"]:
            status["status"] = False
            status["messages"].append(status_cloro_residual_livre["message"])

        if not status_turbidez["status"]:
            status["status"] = False
            status["messages"].append(status_turbidez["message"])

        if not status_coliformes["status"]:
            status["status"] = False
            status["messages"].append(status_coliformes["message"])

        if not status_escherichia["status"]:
            status["status"] = False
            status["messages"].append(status_escherichia["message"])

        if not status_temperatura["status"]:
            # status["status"] = False
            status["messages"].append(status_temperatura["message"])

        if not status["status"]:
            return status

        return {
            "status": True,
            "messages": ["Qualidade adequada para uso"]
        }

    def analise_temperatura(self):
        referencia = ParametrosReferencia.objects.last()

        if referencia.min_temperatura:
            if self.temperatura < referencia.min_temperatura:
                return {
                    "status": True,
                    "message": f"Temperatura {(referencia.min_temperatura - self.temperatura):.2f} °C abaixo do mínimo"
                }
        if referencia.max_temperatura:
            if self.temperatura > referencia.max_temperatura:
                return {
                    "status": True,
                    "message": f"Temperatura {(self.temperatura - referencia.max_temperatura):.2f} °C acima do máximo"
                }
        return {
            "status": True,
            "message": "Temperatura adequada"
        }

    def analise_cloro_residual_livre(self):
        referencia = ParametrosReferencia.objects.last()

        if referencia.min_cloro_residual_livre:
            if self.cloro_residual_livre < referencia.min_cloro_residual_livre:
                return {
                    "status": False,
                    "message": f"Cloro residual livre {(referencia.min_cloro_residual_livre - self.cloro_residual_livre):.2f} mg/L abaixo do mínimo"
                }
        if referencia.max_cloro_residual_livre:
            if self.cloro_residual_livre > referencia.max_cloro_residual_livre:
                return {
                    "status": False,
                    "message": f"Cloro residual livre {(self.cloro_residual_livre - referencia.max_cloro_residual_livre):.2f} mg/L acima do máximo"
                }

        return {
            "status": True,
            "message": "Cloro residual livre adequado"
        }

    def analise_turbidez(self):
        referencia = ParametrosReferencia.objects.last()

        if referencia.min_turbidez:
            if self.turbidez < referencia.min_turbidez:
                return {
                    "status": False,
                    "message": f"Turbidez {(referencia.min_turbidez - self.turbidez):.2f} uT abaixo do mínimo"
                }
        if referencia.max_turbidez:
            if self.turbidez > referencia.max_turbidez:
                return {
                    "status": False,
                    "message": f"Turbidez {(self.turbidez - referencia.max_turbidez):.2f} uT acima do máximo"
                }

        return {
            "status": True,
            "message": "Turbidez adequada"
        }

    def analise_coliformes(self):
        referencia = ParametrosReferencia.objects.last()

        if self.coliformes_totais == referencia.coliformes_totais:
            return {
                "status": True,
                "message": "Ausência de coliformes totais"
            }
        else:

            return {
                "status": False,
                "message": "Presença de coliformes totais"
            }

    def analise_escherichia(self):
        referencia = ParametrosReferencia.objects.last()

        if self.escherichia == referencia.escherichia:
            return {
                "status": True,
                "message": "Ausência de escherichia coli"
            }
        else:
            return {
                "status": False,
                "message": "Presença de escherichia coli"
            }

    @classmethod
    def get_csv(cls, coletas):
        field_names = [field.name for field in cls._meta.fields]
        csv_data = ""
        for coleta in coletas:
            csv_data += ",".join([str(getattr(coleta, field))
                                 for field in field_names]) + "\n"
        return csv_data

    def save(self, *args, **kwargs):
        analise = self.analise()

        self.status = analise.get("status")
        self.status_message = ', '.join(analise.get("messages")) + "."

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Coleta {self.id}"
