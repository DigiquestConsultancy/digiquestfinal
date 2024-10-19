from django.contrib import admin

from .models import PatientDocumentById, PatientPrescriptionFile, PatientRecord, PatientRegister, PatientDetails,PatientPrescription, PatientVarryDetails

admin.site.register(PatientDetails)
@admin.register(PatientRegister)
class PatientRegisterAdmin(admin.ModelAdmin):
    list_display = ('id','mobile_number')
admin.site.register(PatientPrescription)
admin.site.register(PatientVarryDetails)
admin.site.register(PatientDocumentById)
admin.site.register(PatientRecord)
admin.site.register(PatientPrescriptionFile)
