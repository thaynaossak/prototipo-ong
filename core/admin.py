from django.contrib import admin
from .models import Family,Member,Attendance
# Domain changes use the validated service/forms; read-only audit in admin.
class ReadOnly(admin.ModelAdmin):
    def has_add_permission(self,request): return False
    def has_change_permission(self,request,obj=None): return False
    def has_delete_permission(self,request,obj=None): return False
admin.site.register([Family,Member,Attendance],ReadOnly)
