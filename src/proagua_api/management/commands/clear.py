import os
import shutil
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection

class Command(BaseCommand):
    help = 'Reset migrations and delete the PostgreSQL database'

    def handle(self, *args, **options):
        migrations_path = os.path.join('src', 'proagua_api', 'migrations')
        if os.path.exists(migrations_path):
            shutil.rmtree(migrations_path)
            self.stdout.write(self.style.SUCCESS("Pasta migrations excluída com sucesso."))
        with connection.cursor() as cursor:

            cursor.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')
            self.stdout.write(self.style.SUCCESS("Banco de dados PostgreSQL deletado com sucesso."))

if __name__ == '__main__':
    command = Command()
    command.handle()