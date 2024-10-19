from django.utils import timezone
from datetime import timedelta
from celery import shared_task
from django.core.mail import send_mail
from doctor.models import DoctorRegister

@shared_task
def check_trial_expiry():
    print("Hello Sundram")  # Print message to the terminal
    now = timezone.now()  
    expiry_date = now - timedelta(days=15)
    
    doctors = DoctorRegister.objects.filter(
        is_verified=True,
        is_updated__lte=expiry_date,
        is_active=True
    )
    
    for doctor in doctors:
        send_mail(
            'Trial Version Expired',
            'Your trial version has ended. Please consider upgrading your account.',
            'arpitapandey022@gmail.com',
            [doctor.email],
            fail_silently=False,
        )
