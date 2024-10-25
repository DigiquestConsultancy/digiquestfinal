from django.db.models.signals import post_save
from django.dispatch import receiver

from digiadmin.models import hash_value
from .models import ClinicRegister
from .utils import clinic_register_msg91, generate_strong_password, clinic_clinic_register




@receiver(post_save, sender=ClinicRegister)
def notify_if_clinic_register(sender, instance, created, **kwargs):
    if created:
        strong_password = generate_strong_password()
        password_encrypt = hash_value(strong_password)
        instance.password = password_encrypt
        instance.save(update_fields=['password'])
        clinic_mobile_number = instance.mobile_number
        msg91_response = clinic_register_msg91(clinic_mobile_number, strong_password)
        aisensy_response = clinic_clinic_register(clinic_mobile_number, strong_password)

        if msg91_response:
            print("Text message sent successfully!")
        else:
            print("Failed to send Text message.")
        if aisensy_response:
            print("Whatsapp message sent successfully!")
        else:
            print("Failed to send Whatsapp message.")