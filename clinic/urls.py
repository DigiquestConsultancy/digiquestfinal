from django.urls import path



from clinic.views import AppointmentDetailsByClinicID, BookpAppointmentByClinic, ClinicByDoctorId, ClinicDetail,  ClinicRegisters, CountAvailableSlots, DoctorDetailByClinicId, PatientDetailsByClinic, SearchClinic, SearchPatient



urlpatterns = [
    path("register/",ClinicRegisters.as_view()),
    # path("login/",SubdocterLoginApi.as_view()),
    path("details/",ClinicDetail.as_view()),
    path("detailsbyid/",ClinicByDoctorId.as_view()),
    path("appointmentbyclinicid/",AppointmentDetailsByClinicID.as_view()),
    path("patientdetailbyclinic/",PatientDetailsByClinic.as_view()),
    path("doctordetailbyclinicid/",DoctorDetailByClinicId.as_view()),
    path("bookappointmentbyclinic/",BookpAppointmentByClinic.as_view()),
    path("clinicsearch/",SearchClinic.as_view()),
    path("patientsearch/",SearchPatient.as_view()),
    path("countavailableslots/",CountAvailableSlots.as_view()),
]