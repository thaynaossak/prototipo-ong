import uuid
from datetime import timedelta
from django.test import TestCase,Client,override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core import signing,mail
from django.db import IntegrityError,transaction
from django.urls import reverse
from django.utils import timezone
from .models import Family,Member,Attendance
from .forms import AttendanceForm
from .services import record_attendance,mark_absent
@override_settings(STORAGES={'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},'staticfiles':{'BACKEND':'django.contrib.staticfiles.storage.StaticFilesStorage'}},SECURE_SSL_REDIRECT=False,SESSION_COOKIE_SECURE=False,CSRF_COOKIE_SECURE=False)
class FlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('setup_roles',verbosity=0)
        cls.user=get_user_model().objects.create_user('colaborador',password='Teste-exclusivo-123!')
        cls.user.groups.add(Group.objects.get(name='Colaborador'))
        cls.manager=get_user_model().objects.create_user('gestor',password='Teste-exclusivo-123!')
        cls.manager.groups.add(Group.objects.get(name='Gestor'))
        cls.family=Family.objects.create(address='Rua Fictícia',status='active')
        Member.objects.create(family=cls.family,name='Marina Exemplo',birth_date='1990-01-01',relationship='Responsável',responsible=True)
    def setUp(self): self.client.force_login(self.user)
    def data(self,key=None): return {'date':timezone.localdate(),'status':'delivered','baskets':1,'milk':2,'token':signing.dumps({'family':self.family.pk,'user':self.user.pk,'key':str(key or uuid.uuid4())},salt='delivery')}
    def family_data(self): return {'address':'Rua Fictícia','phone':'','members-TOTAL_FORMS':'1','members-INITIAL_FORMS':'0','members-MIN_NUM_FORMS':'1','members-MAX_NUM_FORMS':'20','members-0-name':'Pessoa Modelo','members-0-birth_date':'1995-01-01','members-0-relationship':'Responsável','members-0-responsible':'on'}
    def test_anonymous_denied(self):
        self.client.logout();self.assertEqual(self.client.get('/').status_code,302)
    def test_search_and_history_render(self):
        self.assertContains(self.client.get('/?q=Marina'),'Marina Exemplo')
        self.assertContains(self.client.get(reverse('detail',args=[self.family.pk])),'Histórico')
    def test_delivery_persists_idempotently(self):
        data=self.data();url=reverse('delivery',args=[self.family.pk])
        self.assertRedirects(self.client.post(url,data),reverse('detail',args=[self.family.pk]))
        self.client.post(url,data);self.assertEqual(Attendance.objects.count(),1)
        self.assertEqual(Attendance.objects.get().user,self.user)
    def test_forged_token_rejected(self):
        data=self.data();data['token']='alterado'
        self.assertContains(self.client.post(reverse('delivery',args=[self.family.pk]),data),'inválida ou expirada')
        self.assertEqual(Attendance.objects.count(),0)
    def test_zero_negative_and_future_invalid(self):
        for changes in [{'baskets':0,'milk':0},{'baskets':-1},{'date':timezone.localdate()+timedelta(days=1)}]:
            data=self.data();data.update(changes);self.assertFalse(AttendanceForm(data).is_valid())
    def test_schedule_then_absence_keeps_family_active(self):
        data=self.data();data.update(status='planned',baskets=0,milk=0)
        self.client.post(reverse('delivery',args=[self.family.pk]),data)
        a=Attendance.objects.get();self.client.post(reverse('absent',args=[a.pk]))
        a.refresh_from_db();self.family.refresh_from_db();self.assertEqual(a.status,'absent');self.assertEqual(self.family.status,'active')
    def test_cannot_mark_delivery_absent(self):
        a,_=record_attendance(self.family,self.user,self.data(),uuid.uuid4())
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError): mark_absent(a)
    def test_waitlist_manager_only(self):
        url=reverse('status',args=[self.family.pk]);self.assertEqual(self.client.post(url,{'status':'waiting'}).status_code,403)
        self.client.force_login(self.manager);self.client.post(url,{'status':'waiting'})
        self.assertContains(self.client.get('/?waiting=1'),'Marina Exemplo')
    def test_read_only_status_get_rejected(self): self.assertEqual(self.client.get(reverse('absent',args=[1])).status_code,405)
    def test_family_create_and_no_partial_on_invalid(self):
        d=self.family_data();self.client.post(reverse('create'),d);self.assertEqual(Family.objects.count(),2)
        d['members-0-responsible']='';self.client.post(reverse('create'),d);self.assertEqual(Family.objects.count(),2)
    def test_duplicate_requires_confirmation(self):
        d=self.family_data();d.update({'members-0-name':'Marina Exemplo','members-0-birth_date':'1990-01-01'})
        self.assertContains(self.client.post(reverse('create'),d),'Possível duplicidade');self.assertEqual(Family.objects.count(),1)
        d['confirm_duplicate']='yes';self.client.post(reverse('create'),d);self.assertEqual(Family.objects.count(),2)
    def test_update_retains_history(self):
        record_attendance(self.family,self.user,self.data(),uuid.uuid4())
        d=self.family_data();m=self.family.members.get();d.update({'members-INITIAL_FORMS':'1','members-0-id':m.pk,'members-0-family':self.family.pk,'members-0-name':m.name,'members-0-birth_date':'1990-01-01','address':'Endereço atualizado'})
        self.client.post(reverse('edit',args=[self.family.pk]),d);self.family.refresh_from_db()
        self.assertEqual(self.family.responsible.name,'Marina Exemplo');self.assertEqual(self.family.address,'Endereço atualizado');self.assertEqual(self.family.attendances.count(),1)
    def test_html_rejected_and_sql_is_data(self):
        d=self.family_data();d['address']='<script>alert(1)</script>'
        self.client.post(reverse('create'),d);self.assertEqual(Family.objects.count(),1)
        self.assertEqual(self.client.get("/?q=' OR 1=1 --").status_code,200)
    def test_csrf_required(self):
        c=Client(enforce_csrf_checks=True);c.force_login(self.user)
        self.assertEqual(c.post(reverse('delivery',args=[self.family.pk]),self.data()).status_code,403)
    def test_idle_logout(self):
        s=self.client.session;s['last_activity']=0;s.save();self.assertEqual(self.client.get('/').status_code,302)
    def test_password_hash_and_logout(self):
        self.assertTrue(self.user.password.startswith('pbkdf2_sha256$'))
        self.assertNotIn('Teste-exclusivo',self.user.password)
        self.client.post(reverse('logout'));self.assertEqual(self.client.get('/').status_code,302)
    def test_db_constraints(self):
        with self.assertRaises(IntegrityError),transaction.atomic():
            Member.objects.create(family=self.family,name='Outro',birth_date='1990-01-01',relationship='Responsável',responsible=True)
    def test_security_headers(self):
        r=self.client.get('/');self.assertIn("script-src 'self'",r['Content-Security-Policy']);self.assertEqual(r['Cache-Control'],'no-store')
    def test_no_permission_direct_url(self):
        u=get_user_model().objects.create_user('sem_permissao');self.client.force_login(u)
        self.assertEqual(self.client.get(reverse('delivery',args=[self.family.pk])).status_code,403)
    def test_login_lockout(self):
        self.client.logout()
        for _ in range(5): self.client.post(reverse('login'),{'username':'colaborador','password':'errada'})
        self.assertEqual(self.client.post(reverse('login'),{'username':'colaborador','password':'Teste-exclusivo-123!'}).status_code,429)
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_password_reset_single_use(self):
        self.user.email='teste@example.invalid';self.user.save()
        self.client.post(reverse('password_reset'),{'email':self.user.email})
        self.assertEqual(len(mail.outbox),1)

    def test_excessive_baskets_rejected_without_write(self):
        data=self.data();data['baskets']=2147483648
        response=self.client.post(reverse('delivery',args=[self.family.pk]),data)
        self.assertEqual(response.status_code,200)
        self.assertContains(response,'9999')
        self.assertEqual(Attendance.objects.count(),0)

    def test_health_allows_anonymous_without_personal_data(self):
        self.client.logout()
        r=self.client.get(reverse('health'))
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json(),{'status':'ok'})

    def test_health_returns_503_without_technical_details(self):
        from unittest.mock import patch
        from django.db import OperationalError
        with patch('core.views.connection.cursor',side_effect=OperationalError('secret-connection-detail')):
            r=self.client.get(reverse('health'))
        self.assertEqual(r.status_code,503)
        self.assertEqual(r.json(),{'status':'unavailable'})

    @override_settings(DEBUG=False)
    def test_bootstrap_admin_does_not_reset_existing_password(self):
        import os
        from unittest.mock import patch
        with patch.dict(os.environ,{'DJANGO_SUPERUSER_USERNAME':'initial_admin','DJANGO_SUPERUSER_PASSWORD':'Temporary-test-12345!'}):
            call_command('bootstrap_admin',verbosity=0)
            u=get_user_model().objects.get(username='initial_admin');old=u.password
            call_command('bootstrap_admin',verbosity=0)
            u.refresh_from_db();self.assertEqual(u.password,old)
            self.assertTrue(u.is_superuser)
