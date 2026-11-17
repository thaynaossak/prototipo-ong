from django.urls import path
from . import views
urlpatterns=[path('health/',views.health,name='health'),path('',views.families,name='families'),path('familias/nova/',views.family_edit,name='create'),path('familias/<int:pk>/',views.family_detail,name='detail'),path('familias/<int:pk>/editar/',views.family_edit,name='edit'),path('familias/<int:pk>/entrega/',views.delivery,name='delivery'),path('familias/<int:pk>/situacao/',views.change_status,name='status'),path('atendimentos/<int:pk>/ausencia/',views.absent,name='absent')]
