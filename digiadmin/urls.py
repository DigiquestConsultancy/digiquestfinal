from django.urls import path
from digiadmin.views import ActiveDoctors,  CountDoctors, DigiAdminLoginAPIView, InactiveDoctors, RegisteredDoctors, RequestPassword, ResetPasswordView, UnVerifiedDoctors, VerifiedDoctors, ViewDocDetails, ViewDoctorDocument
 
urlpatterns = [
    path('adminlogin/', DigiAdminLoginAPIView.as_view(), name='adminlogin'),
    path('requestpassword/', RequestPassword.as_view()),
    path('resetpassword/', ResetPasswordView.as_view()),
    path('countdoctors/',CountDoctors.as_view(), name= 'countdoctors'),
    path('activedoctors/', ActiveDoctors.as_view()),
    path('inactivedoctors/', InactiveDoctors.as_view()),
    path('verifieddoctors/', VerifiedDoctors.as_view()),
    path('unverifieddoctors/', UnVerifiedDoctors.as_view()),
    path("admin/", ViewDocDetails.as_view()),
    path('registereddoctors/', RegisteredDoctors.as_view()),
    path('viewdoc/', ViewDoctorDocument.as_view()),
    
]