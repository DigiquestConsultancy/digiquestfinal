from django.db import models


class BookSlot(models.Model):
    patient = models.ForeignKey('patient.PatientDetails', on_delete=models.CASCADE)
    doctor = models.ForeignKey('doctor.DoctorDetail',on_delete=models.CASCADE)
    APPOINTMENT_STATUS_CHOICES = (
        ('upcoming', 'upcoming'),
        ('confirmed', 'Confirmed'),
        ('canceled', 'Canceled'),
        
    )
    appointment_status = models.CharField(max_length=10, choices=APPOINTMENT_STATUS_CHOICES, default='upcoming')
    appointment_slot = models.ForeignKey('doctorappointment.Appointmentslots',on_delete=models.CASCADE)