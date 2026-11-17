from datetime import date
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Family,Member
class Command(BaseCommand):
    help='Insere somente famílias fictícias. Não cria contas ou senhas.'
    @transaction.atomic
    def handle(self,*args,**o):
        for i,name in enumerate(['Marina Exemplo','Carlos Demonstração','Lia Modelo']):
            if Member.objects.filter(name=name).exists(): continue
            f=Family.objects.create(address='Rua Fictícia, número demonstrativo',status='waiting' if i==2 else 'active')
            Member.objects.create(family=f,name=name,birth_date=date(1990+i,1,1),relationship='Responsável',responsible=True)
        self.stdout.write('Dados fictícios preparados.')
