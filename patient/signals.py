from django.db.models.signals import post_save
from django.dispatch import receiver
from digiadmin.models import hash_value
from patient.models import PatientRegister
from patient.utils import congratulation_msg_when_patient_register_aisensy, congratulation_msg_when_patient_register_msg91, generate_strong_password_patient  
from doctorappointment.models import Appointmentslots



# @receiver(post_save, sender=PatientRegister)
# def notify_if_patient_register(sender, instance, created, **kwargs):
#     if created:
#         patient_mobile_number = instance.mobile_number
        
#         response_aisensy = congratulation_msg_when_patient_register_aisensy(patient_mobile_number=patient_mobile_number)
#         response_msg91 = congratulation_msg_when_patient_register_msg91(patient_mobile_number=patient_mobile_number)
        
#         if response_aisensy:
#             print("WhatsApp message sent successfully!")
#         else:
#             print("Failed to send WhatsApp message.")
        
#         if response_msg91:
#             print("msg91 message sent successfully!")
#         else:
#             print("Failed to send msg91 message.")


# @receiver(post_save, sender=PatientRegister)
# def notify_if_reception_register(sender, instance, created, **kwargs):
#     if created:
#         # Check if a password is already set
#         if not instance.password:
#             strong_password = generate_strong_password_patient()
#             password_encrypt = hash_value(strong_password)
#             instance.password = password_encrypt
#             instance.save(update_fields=['password'])
#         else:
#             strong_password = None  # No new password generated if already exists
        
#         patient_mobile_number = instance.mobile_number

#         # Send registration notifications
#         # response_clinic = clinic_register_aisensy(reception_mobile_number=reception_mobile_number, strong_password=strong_password)
#         response_msg91 = congratulation_msg_when_patient_register_msg91(patient_mobile_number=patient_mobile_number, strong_password=strong_password)
        
#         # if response_clinic:
#         #     print("Reception registration successful!")
#         # else:
#         #     print("Failed to register with reception.")
        
#         if response_msg91:
#             print("WhatsApp message sent successfully!")
#         else:
#             print("Failed to send WhatsApp message.")





@receiver(post_save, sender=PatientRegister)
def notify_if_reception_register(sender, instance, created, **kwargs):
    if created:
        # Check if a password is already set
        if not instance.password:
            strong_password = generate_strong_password_patient()
            password_encrypt = hash_value(strong_password)
            instance.password = password_encrypt
            instance.save(update_fields=['password'])
            strong_password_to_send = strong_password  # Use the newly generated password
        else:
            strong_password_to_send = decrypt_value(instance.password)  # Decrypt the existing password
        
        patient_mobile_number = instance.mobile_number

        # Send registration notifications
        # response_clinic = clinic_register_aisensy(reception_mobile_number=reception_mobile_number, strong_password=strong_password_to_send)
        response_msg91 = congratulation_msg_when_patient_register_msg91(patient_mobile_number=patient_mobile_number, strong_password=strong_password_to_send)

        # if response_clinic:
        #     print("Reception registration successful!")
        # else:
        #     print("Failed to register with reception.")
        
        if response_msg91:
            print("WhatsApp message sent successfully!")
        else:
            print("Failed to send WhatsApp message.")
