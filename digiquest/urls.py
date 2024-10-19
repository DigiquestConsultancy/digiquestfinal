
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('patient/', include('patient.urls')),
    path('doctor/', include('doctor.urls')),
    path('subdoctor/', include('subdoctor.urls')),
    path('clinic/', include('clinic.urls')),
    path('reception/', include('reception.urls')),
    path('doctorappointment/', include('doctorappointment.urls')),
    path('patientappointment/', include('patientappointment.urls')),
    path('digiadmin/', include('digiadmin.urls')),
]

if settings.DEBUG:  # Serve static and media files in development mode
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
