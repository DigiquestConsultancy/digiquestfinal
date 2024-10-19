from django.db import models


class Appointmentslots(models.Model):
    doctor = models.ForeignKey('doctor.PersonalsDetails', on_delete=models.CASCADE)  
    appointment_date=models.DateField()
    appointment_slot = models.TimeField()
    is_booked = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    appointment_type = models.CharField(max_length=20, choices=[('walk-in', 'Walk-In'), ('online', 'Online'), ('follow-up', 'Follow-Up')], default='online')
    booked_by=models.ForeignKey('patient.PatientVarryDetails', on_delete=models.CASCADE, null=True,  blank=True)
    is_complete = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)
    is_patient= models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False , null=True, blank=True)  
    consultation_type = models.CharField(max_length=20, choices=[('walk-in', 'Walk-In'), ('online', 'Online')], default='walk-in')