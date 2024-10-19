from django.db.models.signals import post_save
from django.dispatch import receiver

from digiadmin.models import hash_value
from .models import ReceptionRegister
from .utils import  clinic_register_aisensy, generate_strong_password,  reception_register_msg91

@receiver(post_save, sender=ReceptionRegister)
def notify_if_reception_register(sender, instance, created, **kwargs):
    if created:
        strong_password = generate_strong_password()
        password_encrypt= hash_value(strong_password)
        instance.password = strong_password
        instance.save(update_fields=['password'])
        reception_mobile_number = instance.mobile_number
        
        response_clinic = clinic_register_aisensy(reception_mobile_number=reception_mobile_number, strong_password=strong_password)
        response_msg91 = reception_register_msg91(reception_mobile_number=reception_mobile_number, strong_password=strong_password)
        if response_clinic:
            print("reception registration successful!")
        else:
            print("Failed to register with reception.")
        if response_msg91:
            print("WhatsApp message sent successfully!")
        else:
            print("Failed to send WhatsApp message.")
