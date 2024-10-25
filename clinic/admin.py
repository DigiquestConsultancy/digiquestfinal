from django.contrib import admin

# Register your models here.
from django.contrib import admin

from clinic.models import ClinicDetails, ClinicRegister


@admin.register(ClinicDetails)
class ClinicDetailsAdmin(admin.ModelAdmin):
    list_display=('name','clinic_number')
    
    def clinic_number(self, obj):
        return obj.clinic.mobile_number 
    
    

@admin.register(ClinicRegister)
class ClinicRegisterAdmin(admin.ModelAdmin):
    list_display = ('mobile_number', 'doctor') 