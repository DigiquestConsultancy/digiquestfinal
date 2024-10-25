from twilio.rest import Client
from django.core.cache import cache
import random
import os


def register_otp(mobile_no):
    account_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    my_otp =  ''.join(random.choice('0123456789') for _ in range(6))
    cache.set(mobile_no, my_otp, timeout=600)
    message = client.messages.create(
        body=f"OTP to register with DigiQuest is {my_otp}. This is one time password is valid for 10 minutes. DigiQuest Consultancy Services Pvt Ltd.",
        from_=os.environ.get('TWILIO_NUMBER'),
        to='+91'+str(mobile_no)
    )
    print(message.sid, my_otp)
    return my_otp

def register_sms(mobile_no):
    account_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    body=f"Mobile no {mobile_no} is successfully registered with DigiQuest. DigiQuest Consultancy Services Pvt Ltd.",
    from_=os.environ.get('TWILIO_NUMBER'),
    to='+91'+str(mobile_no)
    )
    print(message.sid, mobile_no)
    return True

def login_otp(mobile_no):
    account_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    my_otp =  ''.join(random.choice('0123456789') for _ in range(6))
    cache.set(mobile_no, my_otp, timeout=600)
    message = client.messages.create(
        body=f"OTP to Login with DigiQuest is {my_otp}. This is one time password is valid for 10 minutes. DigiQuest Consultancy Services Pvt Ltd.",
        from_=os.environ.get('TWILIO_NUMBER'),
        to='+91'+str(mobile_no)
    )
    print(message.sid, my_otp)
    return my_otp
