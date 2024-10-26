from django.conf import settings
from django.urls import path
from django.conf.urls.static import static


from .views import   Accessibility, ChangePassword, DoctorDetailSummary, DoctorListBySpecialization, OpdDays,  OpdTimeView,PersonalDoctorDetail,DoctorAddress, CountDoctors, DoctorLoginApi, DoctorDetailApi, DoctorFeedbackApi, DoctorLoginThroughPassword, DoctorName, DoctorRegisterApi,  DoctordetailsUsingID, ForgetPassword, SearchDoctor, SelectQualification, SymptomsDetailView, SymptomsSearch,  GetHospitalName, DoctorBook, UserVerification, ViewDoctorDocument



urlpatterns = [
    # path("register/",DoctorRegisterView.as_view()),
    path("userverification/",UserVerification.as_view()),
    path("register/",DoctorRegisterApi.as_view()),
    path("login/",DoctorLoginApi.as_view()),
    path("changepassword/",ChangePassword.as_view()),
    path("doctorlogin/",DoctorLoginThroughPassword.as_view()),
    path("forgetpassword/", ForgetPassword.as_view()),
    path("details/",DoctorDetailApi.as_view()),
    path('detailsbyid/', DoctordetailsUsingID.as_view()),
    path("searchdoctor/",SearchDoctor.as_view()),
    path('qualifications/', SelectQualification.as_view()),
    path("feedback/", DoctorFeedbackApi.as_view(), name='doctor-feedback'),
    path("doctorname/", DoctorName.as_view()),
    path("hospitalname/",GetHospitalName.as_view()),
    path('countdoctors/',CountDoctors.as_view()),
    path('doctorbook/', DoctorBook.as_view()),
    path('symptomssearch/', SymptomsSearch.as_view()),
    path('symptomsdetail/', SymptomsDetailView.as_view()),
    path('opddays/',OpdDays.as_view()),
    path('doctorsummary/', DoctorDetailSummary.as_view()),
    path('doctordetail/', PersonalDoctorDetail.as_view()),
    path('doctoraddres/', DoctorAddress.as_view()),
    path('timeopd/', OpdTimeView.as_view()),
    path('viewdoc/', ViewDoctorDocument.as_view()),
    path('accessibility/', Accessibility.as_view()),
    path('specialization/', DoctorListBySpecialization.as_view()),
 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)