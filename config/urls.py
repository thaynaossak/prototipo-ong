from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path, include
urlpatterns=[path('admin/',admin.site.urls),path('conta/entrar/',auth.LoginView.as_view(),name='login'),path('conta/sair/',auth.LogoutView.as_view(),name='logout'),path('conta/',include('django.contrib.auth.urls')),path('',include('core.urls'))]
