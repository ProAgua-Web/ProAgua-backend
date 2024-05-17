from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Edificacao)
admin.site.register(models.PontoColeta)
admin.site.register(models.Coleta)
admin.site.register(models.SequenciaColetas)
admin.site.register(models.Fluxo)
admin.site.register(models.ParametrosReferencia)