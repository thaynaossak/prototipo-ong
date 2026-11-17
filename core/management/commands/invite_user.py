import secrets
from django.core.management.base import BaseCommand,CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import PasswordResetForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
class Command(BaseCommand):
    help='Cria conta e envia link de definição de senha ao email verificado.'
    def add_arguments(self,p):
        p.add_argument('username');p.add_argument('email');p.add_argument('--role',choices=['Gestor','Colaborador'],default='Colaborador');p.add_argument('--domain',required=True)
    def handle(self,*args,**o):
        try: validate_email(o['email'])
        except ValidationError: raise CommandError('Email inválido.')
        User=get_user_model()
        if User.objects.filter(username=o['username']).exists() or User.objects.filter(email__iexact=o['email']).exists(): raise CommandError('Conta ou email já registrado.')
        try: group=Group.objects.get(name=o['role'])
        except Group.DoesNotExist: raise CommandError('Execute setup_roles primeiro.')
        u=User.objects.create_user(username=o['username'],email=o['email'],password=secrets.token_urlsafe(48));u.groups.add(group)
        form=PasswordResetForm({'email':u.email})
        if form.is_valid():
            form.save(use_https=True,domain_override=o['domain'],email_template_name='registration/password_reset_email.html',subject_template_name='registration/password_reset_subject.txt')
        self.stdout.write('Conta criada; solicitação de definição de senha enviada. Confirme a entrega no provedor SMTP.')
