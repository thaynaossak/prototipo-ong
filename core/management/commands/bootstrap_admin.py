import os
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand,CommandError
class Command(BaseCommand):
    help='Cria o administrador inicial somente se ainda não existir; usa segredo do ambiente.'
    def handle(self,*args,**options):
        name=os.getenv('DJANGO_SUPERUSER_USERNAME','')
        password=os.getenv('DJANGO_SUPERUSER_PASSWORD','')
        if not name or not password: raise CommandError('Configure o administrador inicial no ambiente protegido.')
        User=get_user_model()
        if not User.objects.filter(username=name).exists():
            u=User(username=name,is_staff=True,is_superuser=True)
            validate_password(password,u)
            u.set_password(password);u.save()
        self.stdout.write('Administrador inicial verificado; nenhuma credencial foi exibida.')
