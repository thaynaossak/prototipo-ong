from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group,Permission
class Command(BaseCommand):
    help='Cria perfis de colaborador e gestor sem criar credenciais.'
    def handle(self,*args,**options):
        common=['view_family','add_family','change_family','view_member','add_member','change_member','view_attendance','add_attendance','change_attendance']
        for name,codes in [('Colaborador',common),('Gestor',common+['manage_waitlist'])]:
            group,_=Group.objects.get_or_create(name=name)
            group.permissions.set(Permission.objects.filter(content_type__app_label='core',codename__in=codes))
        self.stdout.write('Perfis configurados.')
