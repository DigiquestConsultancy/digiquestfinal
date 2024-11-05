from django.db.models.signals import post_save
from django.dispatch import receiver
from digiadmin.models import hash_value
from patient.models import PatientRegister
from patient.utils import congratulation_msg_when_patient_register_aisensy, congratulation_msg_when_patient_register_msg91, generate_strong_password_patient, patient_register_aisensy_password, patient_register_msg91_password  






@receiver(post_save, sender=PatientRegister)
def notify_if_patient_register(sender, instance, created, **kwargs):
    if created:
        patient_mobile_number = instance.mobile_number

        if instance.password:  
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
                
        else:
            strong_password = generate_strong_password_patient()
            password_encrypt = hash_value(strong_password)
            instance.password = password_encrypt
            instance.save(update_fields=['password'])  
            
            response_aisensy = patient_register_aisensy_password(patient_mobile_number, strong_password )
            response_msg91 = patient_register_msg91_password(patient_mobile_number, strong_password)

            if response_aisensy:
                print("WhatsApp message sent successfully!")
            else:
                print("Failed to send WhatsApp message.")

            if response_msg91:
                print("msg91 message sent successfully!")
            else:
                print("Failed to send msg91 message.")