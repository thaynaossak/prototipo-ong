import uuid
from django import forms
from django.conf import settings
from django.core import signing
from django.contrib import messages
from django.contrib.auth.decorators import login_required,permission_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Prefetch
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Family,Member,Attendance
from .forms import FamilyForm,Members,AttendanceForm
from .services import record_attendance,mark_absent

def protected(codename): return permission_required('core.'+codename,raise_exception=True)
@login_required
@protected('view_family')
def families(request):
    waiting=request.GET.get('waiting')=='1'
    qs=Family.objects.prefetch_related('members').order_by('requested_at' if waiting else '-pk')
    if waiting: qs=qs.filter(status='waiting')
    q=request.GET.get('q','').strip()[:120]
    if q: qs=qs.filter(members__name__icontains=q).distinct()
    return render(request,'core/families.html',{'page':Paginator(qs,20).get_page(request.GET.get('page')),'q':q,'waiting':waiting})
@login_required
@protected('view_family')
def family_detail(request,pk):
    f=get_object_or_404(Family.objects.prefetch_related('members'),pk=pk)
    rows=f.attendances.select_related('user')
    # History filter is the optional RF09.
    start=request.GET.get('start','');end=request.GET.get('end','')
    if start or end:
        form=forms.DateField()
        try:
            a=form.clean(start);b=form.clean(end)
            if a>b: raise ValidationError('A data final deve ser igual ou posterior à inicial.')
            rows=rows.filter(date__range=(a,b))
        except ValidationError: messages.error(request,'Informe um intervalo de datas válido.');start=end=''
    return render(request,'core/detail.html',{'family':f,'page':Paginator(rows,20).get_page(request.GET.get('page')),'today':timezone.localdate(),'start':start,'end':end})
@login_required
def family_edit(request,pk=None):
    permission='core.change_family' if pk else 'core.add_family'
    if not request.user.has_perm(permission):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    f=get_object_or_404(Family,pk=pk) if pk else Family()
    form=FamilyForm(request.POST or None,instance=f)
    members=Members(request.POST or None,instance=f,prefix='members')
    duplicates=[]
    if request.method=='POST' and form.is_valid() and members.is_valid():
        for mf in members:
            d=mf.cleaned_data
            if d:
                qs=Member.objects.filter(normalized_name=d['name'].casefold(),birth_date=d['birth_date']).exclude(family=f) if f.pk else Member.objects.filter(normalized_name=d['name'].casefold(),birth_date=d['birth_date'])
                duplicates.extend(qs.select_related('family'))
        if not duplicates or request.POST.get('confirm_duplicate')=='yes':
            with transaction.atomic():
                if f.pk:
                    Family.objects.select_for_update().get(pk=f.pk)
                    # Release the old responsible flag before assigning the new one.
                    f.members.filter(responsible=True).update(responsible=False)
                f=form.save()
                for mf in members:
                    if mf.cleaned_data:
                        member=mf.save(commit=False)
                        member.family=f
                        member.save()
            messages.success(request,'Cadastro salvo com sucesso.')
            return redirect('detail',pk=f.pk)
    return render(request,'core/family_form.html',{'form':form,'members':members,'family':f,'duplicates':duplicates})
@login_required
@protected('add_attendance')
def delivery(request,pk):
    f=get_object_or_404(Family,pk=pk)
    initial={'token':signing.dumps({'family':pk,'user':request.user.pk,'key':str(uuid.uuid4())},salt='delivery')}
    form=AttendanceForm(request.POST or None,initial=initial)
    if request.method=='POST' and form.is_valid():
        try:
            payload=signing.loads(form.cleaned_data['token'],salt='delivery',max_age=1800)
            if payload['family']!=pk or payload['user']!=request.user.pk: raise signing.BadSignature
            _,created=record_attendance(f,request.user,form.cleaned_data,uuid.UUID(payload['key']))
        except (signing.BadSignature,ValueError,ValidationError): form.add_error(None,'Solicitação inválida ou expirada. Volte à consulta e reabra o formulário.')
        else:
            messages.success(request,'Atendimento registrado com sucesso.' if created else 'Esta operação já foi registrada. Nenhuma duplicação foi criada.')
            return redirect('detail',pk=pk)
    return render(request,'core/delivery.html',{'form':form,'family':f})
@login_required
@protected('change_attendance')
@require_POST
def absent(request,pk):
    a=get_object_or_404(Attendance,pk=pk)
    try: mark_absent(a)
    except ValidationError as e: messages.error(request,e.messages[0])
    else: messages.success(request,'Ausência registrada. A situação familiar foi preservada.')
    return redirect('detail',pk=a.family_id)
@login_required
@protected('manage_waitlist')
@require_POST
def change_status(request,pk):
    f=get_object_or_404(Family,pk=pk);status=request.POST.get('status')
    if status not in Family.Status.values: messages.error(request,'Situação inválida.')
    else: f.status=status;f.save(update_fields=['status','updated_at']);messages.success(request,'Situação atualizada pelo gestor.')
    return redirect('detail',pk=pk)
