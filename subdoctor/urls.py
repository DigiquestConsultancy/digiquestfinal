from django.urls import path



from subdoctor.views import AllSubdoctorDetail, SubSubdoctorDetailApi, SubdocterLoginApi, SubdoctorRegisterApi



urlpatterns = [
    path("register/",SubdoctorRegisterApi.as_view()),
    path("login/",SubdocterLoginApi.as_view()),
    path("details/",SubSubdoctorDetailApi.as_view()),
    path("detailsusingdoctormobile/",AllSubdoctorDetail.as_view()),
    
    
]