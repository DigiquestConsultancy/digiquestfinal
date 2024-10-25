from django.contrib import admin

from .models import  DoctorRegister, OpdDays, PersonalsDetails, Qualification, Symptoms, SymptomsDetail
@admin.register(PersonalsDetails)
class DoctorDetailsAdmin(admin.ModelAdmin):
    list_display=('id','name','mobile_number')
    
    def mobile_number(self, obj):
        return obj.doctor.mobile_number

@admin.register(DoctorRegister)
class DoctorRegisterAdmin(admin.ModelAdmin):
    list_display = ('id','mobile_number','is_doctor','is_verified','is_active')
 
admin.site.register(Qualification)
admin.site.register(Symptoms)
admin.site.register(SymptomsDetail)
admin.site.register(OpdDays)

