from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Attendance
@transaction.atomic
def record_attendance(family,user,data,key):
    # Serializes writes per family, including retries, on PostgreSQL.
    type(family).objects.select_for_update().get(pk=family.pk)
    old=Attendance.objects.filter(operation_key=key).first()
    if old:
        if old.family_id!=family.pk or old.user_id!=user.pk: raise ValidationError('Operação inválida.')
        return old,False
    delivered=data['status']=='delivered'
    return Attendance.objects.create(family=family,user=user,date=data['date'],status=data['status'],baskets=data['baskets'],milk=data['milk'],delivered_at=timezone.now() if delivered else None,operation_key=key),True
@transaction.atomic
def mark_absent(attendance):
    a=Attendance.objects.select_for_update().get(pk=attendance.pk)
    if a.status!='planned' or a.date>timezone.localdate(): raise ValidationError('Somente um atendimento previsto, com data já alcançada, pode ser marcado como ausente.')
    a.status='absent';a.save(update_fields=['status'])
