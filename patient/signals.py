from django.db.models.signals import post_save
from django.dispatch import receiver
from patient.models import PatientRegister
from patient.utils import congratulation_msg_when_patient_register_aisensy, congratulation_msg_when_patient_register_msg91  
from doctorappointment.models import Appointmentslots



@receiver(post_save, sender=PatientRegister)
def notify_if_patient_register(sender, instance, created, **kwargs):
    if created:
        patient_mobile_number = instance.mobile_number
        
        response_aisensy = congratulation_msg_when_patient_register_aisensy(patient_mobile_number=patient_mobile_number)
        response_msg91 = congratulation_msg_when_patient_register_msg91(patient_mobile_number=patient_mobile_number)
        
        if response_aisensy:
            print("WhatsApp message sent successfully!")
        else:
            print("Failed to send WhatsApp message.")
       
        if response_msg91:
            print("msg91 message sent successfully!")
        else:
            print("Failed to send msg91 message.")
