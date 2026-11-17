import re
from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils import timezone
from .models import Family, Member, Attendance

def plain(value):
    if re.search(r'[<>]',value): raise forms.ValidationError('Use somente texto, sem marcação HTML.')
    return value.strip()
class FamilyForm(forms.ModelForm):
    class Meta: model=Family; fields=['address','phone']
    def clean_address(self): return plain(self.cleaned_data['address'])
    def clean_phone(self): return plain(self.cleaned_data['phone'])
class MemberForm(forms.ModelForm):
    class Meta:
        model=Member; fields=['name','birth_date','relationship','responsible']
        widgets={'birth_date':forms.DateInput(format='%Y-%m-%d',attrs={'type':'date'})}
    def clean_name(self): return ' '.join(plain(self.cleaned_data['name']).split())
    def clean_relationship(self): return plain(self.cleaned_data['relationship'])
    def clean_birth_date(self):
        d=self.cleaned_data['birth_date']
        if d>timezone.localdate(): raise forms.ValidationError('O nascimento não pode estar no futuro.')
        return d
class MemberSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors): return
        rows=[f.cleaned_data for f in self.forms if f.cleaned_data]
        if sum(bool(d.get('responsible')) for d in rows)!=1: raise forms.ValidationError('Informe exatamente um responsável familiar.')
        keys=[(d['name'].casefold(),d['birth_date']) for d in rows]
        if len(keys)!=len(set(keys)): raise forms.ValidationError('O mesmo integrante aparece duas vezes neste formulário. Revise os dados.')
Members=inlineformset_factory(Family,Member,form=MemberForm,formset=MemberSet,extra=1,can_delete=False,min_num=1,validate_min=True,max_num=20,validate_max=True,absolute_max=20)
class AttendanceForm(forms.Form):
    date=forms.DateField(label='Data prevista / entrega',initial=timezone.localdate,widget=forms.DateInput(attrs={'type':'date'}))
    status=forms.ChoiceField(label='Operação',choices=[('delivered','Registrar entrega'),('planned','Agendar atendimento')])
    baskets=forms.IntegerField(label='Quantidade de cestas',min_value=0,max_value=9999,initial=0)
    milk=forms.DecimalField(label='Leite em litros',min_value=0,max_value=999999,decimal_places=1,initial=0)
    token=forms.CharField(widget=forms.HiddenInput)
    def clean(self):
        d=super().clean()
        if d.get('status')=='delivered':
            if d.get('date') and d['date']>timezone.localdate(): self.add_error('date','Uma entrega realizada não pode ter data futura.')
            if not (d.get('baskets',0) or d.get('milk',0)): raise forms.ValidationError('Informe quantidade positiva em pelo menos um item.')
        elif d.get('baskets') or d.get('milk'): raise forms.ValidationError('Agendamentos devem ter quantidades zeradas; os itens serão informados na entrega.')
        return d
