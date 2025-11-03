import os
import shutil
import django
from django.core.management import call_command
from django.core.management.base import BaseCommand

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

class Command(BaseCommand):
    help = 'Reset data into the database.'

    def handle(self, *args, **options):
        try:
            # Executar comandos do Django
            call_command('makemigrations', 'proagua_api')
            call_command('migrate')
            call_command('createadmin')

            self.stdout.write(self.style.SUCCESS('Tarefas concluídas com sucesso.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao executar a tarefa: {e}'))
