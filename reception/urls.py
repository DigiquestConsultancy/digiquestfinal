from django.urls import path



from reception.views import AppointmentDetailsByReceptionID, DoctorDetailByReceptionId, RceptionSearch, ReceptionDetail, ReceptionDetailsByDoctorId,ReceptionRegisters, BookByReception,AvailableWalkInSlotsCount, ShowAllAppointments



urlpatterns = [
    path("register/",ReceptionRegisters.as_view()),
    # path("login/",SubdocterLoginApi.as_view()),
    path("details/",ReceptionDetail.as_view()),
    path("detailsbydoctorid/",ReceptionDetailsByDoctorId.as_view()),
    path("appointmentbyreceptionid/",AppointmentDetailsByReceptionID.as_view()),
    path("doctordetailsbyreceptionid/", DoctorDetailByReceptionId.as_view()),
    path("receptionsearch/", RceptionSearch.as_view()),
    path("BookByReception/", BookByReception.as_view()),
    path("walkincount/", AvailableWalkInSlotsCount.as_view()),
    path("allappointments/", ShowAllAppointments.as_view())
]