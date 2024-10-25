from django.contrib import admin

# Register your models here.
from django.contrib import admin

from reception.models import ReceptionRegister, ReceptionDetails

# Register your models here.
@admin.register(ReceptionRegister)
class ClinicRegisterAdmin(admin.ModelAdmin):
    list_display = ('mobile_number', 'doctor') 
    
admin.site.register(ReceptionDetails)