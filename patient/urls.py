from django.urls import path


from .views import  ForgetPassword, PatientVerification,GetPatientDetailsUsingID, PatientCity, PatientDetailByDoctor, PatientDetailsAPIView, PatientDocumentSearch, PatientDocumentUsingAppointmentID, PatientLoginApiView, PatientNameByID,  PatientRecordView, PrintPatientReport, SearchMyAppointments ,PatientDocumentUpload, PatientFeedbackApi, PatientLoginApi, PatientPrescriptionApi, PatientRegisterApi, PatientDetailApi,  UploadPrescriptionFile, UploadPrescriptionFileView, ViewDocument, ViewDocumentByAppointmentId



urlpatterns = [
    path("register/",PatientVerification.as_view()),
    path("patientregister/",PatientRegisterApi.as_view()),
    path("login/",PatientLoginApi.as_view()),
    path("patientlogin/", PatientLoginApiView.as_view()),
    path("details/",PatientDetailApi.as_view()),
    path("location/",PatientCity.as_view()),
    path("patientdetails/",GetPatientDetailsUsingID.as_view()),
    path("patientdocument/",PatientDocumentUpload.as_view()),
    path("patientdocumentsearch/",PatientDocumentSearch.as_view()),
    path("patientpriscription/",PatientPrescriptionApi.as_view()),
    path("feedback/", PatientFeedbackApi.as_view()),
    path("patientdetailbydoctor/",PatientDetailByDoctor.as_view()),
    path("vital/",PatientRecordView.as_view()),
    path("viewdocument/",ViewDocument.as_view()),
    path("patientname/",PatientNameByID.as_view()),
    path("patient/",PatientDetailsAPIView.as_view()),
    path("patientdocumentusingappointmentid/",PatientDocumentUsingAppointmentID.as_view()),
    path("viewdocumentbyid/",ViewDocumentByAppointmentId.as_view()),
    path("patientprescriptonfile/",UploadPrescriptionFile.as_view()),
    path("patientprescriptonfileView/",UploadPrescriptionFileView.as_view()),
    path("forget/", ForgetPassword.as_view()),
    path('printrepport/', PrintPatientReport.as_view()),
]