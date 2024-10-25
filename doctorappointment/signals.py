from urllib import response
from django.db.models.signals import post_save
from django.dispatch import receiver
from clinic.models import ClinicDetails, ClinicRegister
from doctorappointment.models import Appointmentslots
from doctorappointment.utils import appointment_cancel_message_to_doctor_msg91, appointment_confirm_message_to_doctor_msg91, appointment_confirm_message_to_patient_msg91, send_reminder_to_doctor, send_reminder_to_patient, send_whatsapp_booked_msg_doctor, send_whatsapp_booked_msg_to_patient, send_whatsapp_cancel_message
# , send_whatsapp_message
        
# @receiver(post_save, sender=Appointmentslots)
# def notify_if_slot_blocked(sender, instance,created, **kwargs):
#     if instance.is_blocked:
        
#             patient_mobile_number= instance.booked_by.mobile_number
        
#             doctor_name = instance.doctor.name
#             patient_name = instance.booked_by.name
#             booked_date = instance.appointment_date
#             slot_time = instance.appointment_slot
#             hospital_name = instance.doctor.hospital_name
#             # clinic_name = ClinicDetails.objects.get(id=instance.doctor.id)        
#             send_blocked_slot_notification(patient_mobile_number,doctor_name,patient_name,booked_date,slot_time)
            


@receiver(post_save, sender=Appointmentslots)
def notify_if_canceled(sender, instance, created, **kwargs):
    if instance.is_canceled:  # Ensure we're processing updates and not creations
            patient_mobile_number = instance.booked_by.mobile_number
            patient_name = instance.booked_by.name
            clinic_name = "Unknown Clinic"
            doctor_register = instance.doctor.doctor
            opd_instance = doctor_register.opd_set.first()  
            if opd_instance:
                clinic_name = opd_instance.clinic_name   # Ensure `hospital_name` is correct
            doctor_name = instance.doctor.name
            hospital_number=instance.doctor.doctor.mobile_number
            booked_date = instance.appointment_date.strftime('%d-%m-%Y')
            slot_time = instance.appointment_slot.strftime('%H:%M')

            response = send_whatsapp_cancel_message(
                patient_mobile_number=patient_mobile_number,
                patient_name=patient_name,
                hospital_name=clinic_name,
                doctor_name=doctor_name,
                booked_date=booked_date,
                slot_time=slot_time,
                hospital_number=hospital_number
            )
            response = appointment_cancel_message_to_doctor_msg91(
                patient_mobile_number=patient_mobile_number,
                doctor_name=doctor_name,
                booked_date=booked_date,
                slot_time=slot_time,
                hospital_number=hospital_number
            )
            
            if response:
                print("WhatsApp message sent successfully!")
            else:
                print("Failed to send WhatsApp message.")



@receiver(post_save, sender=Appointmentslots)
def notify_when_booked(sender, instance, created, **kwargs):
    if instance.is_booked: 
            patient_mobile_number = instance.booked_by.mobile_number
            patient_name = instance.booked_by.name
            clinic_name = "Unknown Clinic"
            doctor_register = instance.doctor.doctor
            address_instance = doctor_register.address_set.first() 
            opd_instance = doctor_register.opd_set.first()  
            if address_instance:
                clinic_city = address_instance.city
                street_address=address_instance.street_address
                landmark=address_instance.landmark
                pin_code=address_instance.pin_code
                
            if opd_instance:
                clinic_name = opd_instance.clinic_name  
            doctor_name = instance.doctor.name
            hospital_number=instance.doctor.doctor.mobile_number
            booked_date = instance.appointment_date.strftime('%d-%m-%Y')
            slot_time = instance.appointment_slot.strftime('%H:%M')

            response = send_whatsapp_booked_msg_doctor(
                patient_name=patient_name,
                hospital_name=clinic_name,
                doctor_name=doctor_name,
                booked_date=booked_date,
                slot_time=slot_time,
                hospital_number=hospital_number
            )
            response = send_whatsapp_booked_msg_to_patient(
                patient_name=patient_name,
                hospital_name=clinic_name,
                doctor_name=doctor_name,
                booked_date=booked_date,
                slot_time=slot_time,
                patient_mobile_number=patient_mobile_number,
                hospital_number=hospital_number
            )
            response = appointment_confirm_message_to_doctor_msg91(
                booked_date=booked_date,
                patient_name=patient_name,
                slot_time=slot_time,
                hospital_number=hospital_number
            )
            response = appointment_confirm_message_to_patient_msg91(
                doctor_name=doctor_name,
                booked_date=booked_date,
                slot_time=slot_time,
                clinic_city=clinic_city,
                street_address=street_address,
                landmark=landmark,
                pin_code=pin_code,
                patient_mobile_number=patient_mobile_number,
            )
            
            if response:
                print("WhatsApp message sent successfully!")
            else:
                print("Failed to send WhatsApp message.")
                
                
        





@receiver(post_save, sender=Appointmentslots)
def notify_when_booked_patient(sender, instance, created, **kwargs):


    if instance.reminder_sent:
        patient_mobile_number = instance.booked_by.mobile_number
        patient_name = instance.booked_by.name
        clinic_name = "Unknown Clinic"
        doctor_register = instance.doctor.doctor
        opd_instance = doctor_register.opd_set.first()  
        if opd_instance:
            clinic_name = opd_instance.clinic_name  
        doctor_name = instance.doctor.name
        hospital_number = doctor_register.mobile_number 
        booked_date = instance.appointment_date.strftime('%d-%m-%Y')
        slot_time = instance.appointment_slot.strftime('%H:%M')

        response = send_reminder_to_patient(
            patient_name=patient_name,
            hospital_name=clinic_name, 
            doctor_name=doctor_name,
            booked_date=booked_date,
            slot_time=slot_time,
            patient_mobile_number=patient_mobile_number,
            hospital_number=hospital_number
        )
        response = send_reminder_to_doctor(
            patient_name=patient_name,
            hospital_name=clinic_name, 
            doctor_name=doctor_name,
            booked_date=booked_date,
            slot_time=slot_time,
            patient_mobile_number=patient_mobile_number,
            hospital_number=hospital_number
        )
        if response:
            print("WhatsApp message sent successfully!")
        else:
            print("Failed to send WhatsApp message.")