from django.db.models.signals import post_save
from django.dispatch import receiver
from digiadmin.models import hash_value
from doctor.utils import   congratulatin_msg_when_doctor_register_aisensy, congratulatin_msg_when_doctor_register_msg91, doctor_detail, doctor_verification,  send_verification_email, send_verified_email
from doctor.models import  DoctorDetail, DoctorRegister




        
# @receiver(post_save, sender=DoctorDetail)
# def doctor_verification_status(sender, instance, created, **kwargs):
#     if not instance.is_verified:   
#         doctor_mobile_no = instance.doctor.mobile_number
#         print("Doctor's No:", doctor_mobile_no)
#         doctor_verification(doctor_mobile_no)

# @receiver(post_save, sender=DoctorDetail)
# def doctor_detail_status(sender, instance, created, **kwargs):
#     if instance.is_verified:   
#         doctor_mobile_no = instance.doctor.mobile_number
#         print("Doctor's No:", doctor_mobile_no)
#         doctor_detail(doctor_mobile_no)       
        
@receiver(post_save, sender=DoctorDetail)
def send_verification_email_signal(sender, instance, created, **kwargs):
    if created:
        doctor_registration_number = instance.registration_no
        doctor_name = instance.name
        send_verification_email(doctor_registration_number, doctor_name)
        
@receiver(post_save, sender=DoctorDetail)
def doctor_detail_post_save(sender, instance, created, **kwargs):
    if  instance.is_verified:
        doctor_registration_number = instance.registration_no
        doctor_name = instance.name
        send_verified_email(doctor_registration_number, doctor_name)


@receiver(post_save, sender=DoctorRegister)
def notify_if_doctor_register(sender, instance, created, **kwargs):
    if created:
        doctor_mobile_number = instance.mobile_number
        
        response_aisensy = congratulatin_msg_when_doctor_register_aisensy(doctor_mobile_number)
        response_msg91 = congratulatin_msg_when_doctor_register_msg91(doctor_mobile_number)
        
        if response_aisensy:
            print("WhatsApp message sent successfully!")
        else:
            print("Failed to send WhatsApp message.")
        if response_msg91:
            print("msg91 message sent successfully!")
        else:
            print("Failed to send msg91 message.")
