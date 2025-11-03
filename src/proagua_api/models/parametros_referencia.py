from django.db import models

TIPOS_PONTOS = (
    (1, "Bebedouro"),
    (2, "Reservatório predial superior"),
    (3, "Reservatório predial inferior"),
    (4, "Reservatório de distribuição superior"),
    (5, "Reservatório de distribuição inferior"),
    (6, "CAERN")
)


class ParametrosReferencia(models.Model):
    # Está adequado se estiver entre 9,5 °C e 10,5 °C
    min_temperatura = models.FloatField(
        verbose_name="temperatura mínima",
        blank=True,
        null=True,
        default=9.5
    )
    max_temperatura = models.FloatField(
        verbose_name="temperatura máxima",
        blank=True,
        null=True,
        default=10.5
    )

    # Está adequada se estiver entre ou igual a 0,2 mg/L e a 5 mg/L
    min_cloro_residual_livre = models.FloatField(
        verbose_name="cloro residual livre mínimo",
        blank=True,
        null=True,
        default=0.2
    )
    max_cloro_residual_livre = models.FloatField(
        verbose_name="cloro residual livre máximo",
        blank=True,
        null=True,
        default=5.0
    )

    # Está adequada se estiver for ≤ 5 uT
    min_turbidez = models.FloatField(
        verbose_name="turbidez mínima",
        blank=True,
        null=True,
        default=None,
    )
    max_turbidez = models.FloatField(
        verbose_name="turbidez máxima",
        blank=True,
        null=True,
        default=5.0
    )

    min_cor = models.FloatField(
        verbose_name="cor mínima",
        blank=True,
        null=True,
        default=None,
    )
    max_cor = models.FloatField(
        verbose_name="cor máxima",
        blank=True,
        null=True,
        default=None,
    )
    
    # Está adequada se estiver ausente
    coliformes_totais = models.BooleanField(
        verbose_name="coliformes totais",
        blank=False,
        null=False,
        default=False
    )

    # Está adequada se estiver ausente
    escherichia = models.BooleanField(
        verbose_name="escherichia coli",
        blank=False,
        null=False,
        default=False
    )

    def __str__(self) -> str:
        return "Parâmetros de Referência"
