from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seed the database with a default superuser (username: admin, password: admin)'

    def handle(self, *args, **options):
        # Verifique se o superusuário 'admin' já existe
        if not User.objects.filter(username='admin').exists():
            # Crie um superusuário com nome de usuário 'admin' e senha 'admin'
            User.objects.create_superuser('admin', password='admin')
            self.stdout.write(self.style.SUCCESS('Superuser "admin" created with password "admin"'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser "admin" already exists'))