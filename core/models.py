import uuid
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
class Family(models.Model):
    class Status(models.TextChoices):
        REVIEW='review','Aguardando análise'
        ACTIVE='active','Ativa'
        WAITING='waiting','Em espera'
        INACTIVE='inactive','Inativa'
    address=models.CharField('Endereço',max_length=200)
    phone=models.CharField('Telefone (opcional)',max_length=30,blank=True)
    status=models.CharField('Situação',max_length=12,choices=Status.choices,default=Status.REVIEW,db_index=True)
    requested_at=models.DateTimeField('Data da solicitação',auto_now_add=True,db_index=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        permissions=[('manage_waitlist','Gerenciar situação e lista de espera')]
    @property
    def responsible(self): return next((m for m in self.members.all() if m.responsible),None)
    def __str__(self): return f'F{self.pk:04d}'
class Member(models.Model):
    family=models.ForeignKey(Family,on_delete=models.PROTECT,related_name='members')
    name=models.CharField('Nome',max_length=120)
    normalized_name=models.CharField(max_length=120,db_index=True,editable=False)
    birth_date=models.DateField('Data de nascimento')
    relationship=models.CharField('Parentesco',max_length=50)
    responsible=models.BooleanField('Responsável familiar',default=False)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['family'],condition=Q(responsible=True),name='one_responsible_per_family')]
        indexes=[models.Index(fields=['normalized_name','birth_date'])]
    def save(self,*args,**kwargs):
        self.name=' '.join(self.name.split())
        self.normalized_name=self.name.casefold()
        super().save(*args,**kwargs)
    def __str__(self): return self.name
class Attendance(models.Model):
    class Status(models.TextChoices):
        PLANNED='planned','Previsto'
        DELIVERED='delivered','Entregue'
        ABSENT='absent','Ausente'
        CANCELLED='cancelled','Cancelado'
    family=models.ForeignKey(Family,on_delete=models.PROTECT,related_name='attendances')
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
    date=models.DateField('Data prevista / entrega',db_index=True)
    status=models.CharField('Situação',max_length=12,choices=Status.choices,default=Status.PLANNED)
    delivered_at=models.DateTimeField(null=True,blank=True)
    baskets=models.PositiveIntegerField('Quantidade de cestas',default=0)
    milk=models.DecimalField('Leite em litros',max_digits=8,decimal_places=1,default=0,validators=[MinValueValidator(0)])
    operation_key=models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-date','-pk']
        constraints=[models.CheckConstraint(condition=Q(milk__gte=0),name='nonnegative_milk'),models.CheckConstraint(condition=(Q(status='delivered',delivered_at__isnull=False)&(Q(baskets__gt=0)|Q(milk__gt=0)))|(Q(status__in=['planned','absent','cancelled'],baskets=0,milk=0,delivered_at__isnull=True)),name='valid_attendance_state')]
