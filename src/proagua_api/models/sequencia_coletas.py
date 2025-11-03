from django.db import models

class SequenciaColetas(models.Model): 
    id = models.AutoField(primary_key=True)
    amostragem = models.PositiveIntegerField(
        verbose_name="amostragem"
    )
    ponto = models.ForeignKey(
        to="proagua_api.PontoColeta",
        verbose_name="ponto",
        on_delete=models.PROTECT,
    )
    
    class Meta:
        unique_together  = ("amostragem", "ponto")

    def has_dependent_objects(instance):
        for related_object in instance._meta.related_objects:
            related_name = related_object.get_accessor_name()
            related_manager = getattr(instance, related_name)
            if related_manager.exists():
                return True
        return False

    
    def __str__(self) -> str:
        return f"Sequencia Coletas {self.id}"
