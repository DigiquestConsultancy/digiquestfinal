from twilio.rest import Client
from django.core.cache import cache
import os
from django.core.mail import send_mail
from django.conf import settings
import uuid

def send_meeting_link(recipient_emails, appointment_time, appointment_date):
    subject = "Your Online Consultation Meeting Link"
   
    room_name = f"meeting-{uuid.uuid4()}"  
    meeting_link = f"https://meet.jit.si/{room_name}"
 
    message = (f"Hello,\n\n"
               f"You have a new online consultation scheduled on {appointment_date} at {appointment_time}.\n\n"
               f"Please join using the following link:\n{meeting_link}\n\n"
               f"Best regards,\nYour Team"
              )
    
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_emails, fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False   
