from django.urls import path


from .views import BookSlotListView, PatientSlotView,  SearchMyAppointments, SlotDetailsBySlotId


urlpatterns = [
    path("bookslot/",BookSlotListView.as_view()),
    path("viewslot/",PatientSlotView.as_view()),
    path("viewslotbyid/",SlotDetailsBySlotId.as_view()),
    path("searchmyslot/",SearchMyAppointments.as_view()),
]