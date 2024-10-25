from django.contrib import admin

from subdoctor.models import SubdoctorDetail, SubdoctorRegister

# Register your models here.
admin.site.register(SubdoctorDetail)
admin.site.register(SubdoctorRegister)