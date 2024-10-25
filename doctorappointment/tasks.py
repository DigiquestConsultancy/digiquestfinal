from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from .models import Appointmentslots
import logging
import pytz

logger = logging.getLogger('error_doctorappointment')

@shared_task
def send_appointment_reminders():
    logger.info("Task started: send_appointment_reminders")
    ist = pytz.timezone('Asia/Kolkata')
    now = timezone.now().astimezone(ist)  
    reminder_time_start = now  
    reminder_time_end = now + timedelta(minutes=1)  


    appointments = Appointmentslots.objects.filter(
        appointment_date=reminder_time_start.date(),
        consultation_type='online',
        appointment_slot__gte=reminder_time_start.time(),
        appointment_slot__lt=reminder_time_end.time(),
        reminder_sent=False
    )

    logger.info(f"Found {appointments.count()} appointments to update.")

    if appointments.exists():
        for appointment in appointments:
            update_reminder_sent(appointment)
    else:
        logger.info("No appointments found to update.")
        print("No appointments found to update.")

    logger.info("Task completed: send_appointment_reminders")

def update_reminder_sent(appointment):
    try:
        appointment.reminder_sent = True
        appointment.save()
        logger.info(f"Updated reminder_sent for appointment ID: {appointment.id}")
        print(f"Updated reminder_sent for appointment ID: {appointment.id}")

    except Exception as e:
        logger.exception(f"Exception during updating reminder_sent for appointment ID: {appointment.id}: {str(e)}")
        print(f"Exception during updating reminder_sent for appointment ID: {appointment.id}: {str(e)}")









