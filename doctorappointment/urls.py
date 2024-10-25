
from django.urls import path

from doctorappointment.views import BookedAppointments, CanceledAppointment, CompletedAppointment, CountBookedAppointments, CreateMeetLinkView, CurrentDateSlot, DoctorSlotCreate, PatientDetailUpdateByDoctor, SearchBookedAppointments, SlotGetByPatient, TodayAndAfterTodaySlot, TodaysSlot, TotalAppointmentsCount, UnblockSlots


urlpatterns = [
    path('slot/', DoctorSlotCreate.as_view()),
    path('getslot/', BookedAppointments.as_view()),
    path('todayslot/', CurrentDateSlot.as_view()),
    path('blankslot/', SlotGetByPatient.as_view()),
    path('patientdetailupdatebydoctor/', PatientDetailUpdateByDoctor.as_view()),
    # path("searchpatient/",SearchPatientAppointment.as_view()),     
    path('searchslot/', SearchBookedAppointments.as_view()),
    path('slotstoday/', TodaysSlot.as_view()),
    path("countslot/",CountBookedAppointments.as_view()),
    path("todayafterslot/",TodayAndAfterTodaySlot.as_view()),
    path('unblockslot/',UnblockSlots.as_view()),
    path("totalappointmentcount/", TotalAppointmentsCount.as_view()),
    path('completedappointment/', CompletedAppointment.as_view()),
    path("canceledappointment/",CanceledAppointment.as_view()),
    path('meetlink/', CreateMeetLinkView.as_view()),
]