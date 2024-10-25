import http
import json
import secrets
import string
import requests
from twilio.rest import Client
from django.core.cache import cache
import random
import os
from django.core.mail import send_mail


 
AISENSY_API_KEY = os.environ.get('AISENSY_API_KEY')
 

def doctor_verification(phone_no):
    account_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(

        body=f"your verification under process ",
        from_=os.environ.get('TWILIO_NUMBER'),
        to='+91'+str(phone_no)
    )
    print(message.sid,)
    return 
   
def doctor_detail(phone_no):
    account_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"your verification is completed ",
        from_=os.environ.get('TWILIO_NUMBER'),
        to='+91'+str(phone_no)
    )
    print(message.sid,)
    return 

def send_verification_email(doctor_registration_number, doctor_name):
    subject = 'Doctor Verification'
    message = f'A new doctor detail has been uploaded and requires verification.\n\nDoctor Name: {doctor_name}\nDoctor Registration Number: {doctor_registration_number}'
    recipient_email = os.environ.get('RECIPIENT_EMAIL')  
    send_mail(subject, message, None, [recipient_email])

def send_verified_email(doctor_registration_number, doctor_name):
    subject = 'Doctor Verification Completed'
    message = f'The doctor detail has been uploaded and varified.\n\nDoctor Name: {doctor_name}\nDoctor Registration Number: {doctor_registration_number}'
    recipient_email = os.environ.get('RECIPIENT_EMAIL')  
    send_mail(subject, message, None, [recipient_email])



# ===========================Register OTP for doctor using msg91 and aisensy============================


def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choice('0123456789') for _ in range(6))



def register_otp_for_doctor(mobile_no, otp):
    conn = http.client.HTTPSConnection("control.msg91.com")
    
    mobile_no = str(mobile_no)  # Ensure mobile_no is a string
    otp = str(otp)              # Ensure otp is a string
    full_mobile_number = f"91{mobile_no}"
    
    payload = {
        "template_id": "67067aa9d6fc051e6a4a58e2",  
        "short_url": "0",  
        "realTimeResponse": "1",  
        "recipients": [
            {
                "mobiles": full_mobile_number,
                "var1": otp
            }
        ]
    }

    auth_key = os.environ.get('AUTH_KEY')
    if auth_key is None:
        raise ValueError("AUTH_KEY environment variable is not set")

    headers = {
        'authkey': auth_key,  
        'accept': "application/json",
        'content-type': "application/json"
    }

    json_payload = json.dumps(payload)
    print(json_payload)  # Debugging line

    try:
        conn.request("POST", "/api/v5/flow", json_payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        if isinstance(data, bytes):
            return data.decode("utf-8")
        else:
            print("Unexpected response type")
            return None
    except Exception as e:
        print(f"Error sending text message: {e}")
        return None


def send_register_otp_to_doctor(mobile_number, otp):
    """Send OTP to a destination using AISENSY API."""
    AISENSY_API_KEY = os.getenv('AISENSY_API_KEY')
    if not AISENSY_API_KEY:
        return {'success': False, 'message': 'API key not available'}

    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "otp_verification",
        "destination": str(mobile_number),
        "userName": "Your Company Name",
        "templateParams": [otp],
        "source": "registration",
        "buttons": [
            {
                "type": "button",
                "sub_type": "url",
                "index": 0,
                "parameters": [{"type": "text", "text": otp}]
            }
        ]
    }
    url = 'https://backend.aisensy.com/campaign/t1/api/v2'
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        print(f"Aisensy OTP sent successfully to {mobile_number}, OTP: {otp}")
        return {'success': True, 'message': 'Aisensy OTP sent successfully', 'otp': otp}
    except requests.exceptions.RequestException as e:
        print(f"Failed to send OTP via Aisensy: {e}")
        return {'success': False, 'message': 'Failed to send OTP via Aisensy'}
    
    
    
# =============================================================================================




# =====================login otp for doctor  ========================================================



def login_otp_to_doctor(mobile_no, otp):
    conn = http.client.HTTPSConnection("control.msg91.com")
    
    mobile_no = str(mobile_no)  # Ensure mobile_no is a string
    otp = str(otp)              # Ensure otp is a string
    full_mobile_number = f"91{mobile_no}"
    
    payload = {
        "template_id": "6707a157d6fc05081e38d463",  
        "short_url": "0",  
        "realTimeResponse": "1",  
        "recipients": [
            {
                "mobiles": full_mobile_number,
                "var1": otp
            }
        ]
    }

    auth_key = os.environ.get('AUTH_KEY')
    if auth_key is None:
        raise ValueError("AUTH_KEY environment variable is not set")

    headers = {
        'authkey': auth_key,  
        'accept': "application/json",
        'content-type': "application/json"
    }

    json_payload = json.dumps(payload)
    print(json_payload)  # Debugging line

    try:
        conn.request("POST", "/api/v5/flow", json_payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        if isinstance(data, bytes):
            return data.decode("utf-8")
        else:
            print("Unexpected response type")
            return None
    except Exception as e:
        print(f"Error sending text message: {e}")
        return None
    
    
    
    
    
    
    
    


def send_login_otp_to_doctor(mobile_number, otp):
    """Send OTP to a destination using AISENSY API."""
    AISENSY_API_KEY = os.getenv('AISENSY_API_KEY')
    destination= str(mobile_number)
    # Create the payload for the API request
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "otp_verification",
        "destination": destination,
        "userName": "Your Company Name",
        "templateParams": [otp],
        "source": "registration",
        "buttons": [
            {
                "type": "button",
                "sub_type": "url",
                "index": 0,
                "parameters": [
                    {"type": "text", "text": otp}
                ]
            }
        ]
    }
    
    url = 'https://backend.aisensy.com/campaign/t1/api/v2'
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return {'success': 'Aisensy message successfully send OTP', 'otp': otp}
    except requests.exceptions.RequestException as e:
        return {'error': 'Failed to send OTP', 'details': str(e)}
    
    
    
# ===========================Congratulation msg for doctor when register using msg91 and aisensy============================





def congratulatin_msg_when_doctor_register_msg91(doctor_mobile_number):
    conn = http.client.HTTPSConnection("control.msg91.com")
    
    mobile_no = str(doctor_mobile_number) 
    full_mobile_number = f"91{mobile_no}"
    
    payload = {
        "template_id": "670ce005d6fc05471e174d52",  
        "short_url": "0",  
        "realTimeResponse": "1",  
        "recipients": [
            {
                "mobiles": full_mobile_number,
            }
        ]
    }

    auth_key = os.environ.get('AUTH_KEY')
    if auth_key is None:
        raise ValueError("AUTH_KEY environment variable is not set")

    headers = {
        'authkey': auth_key,  
        'accept': "application/json",
        'content-type': "application/json"
    }

    json_payload = json.dumps(payload)
    print(json_payload)  # Debugging line

    try:
        conn.request("POST", "/api/v5/flow", json_payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        if isinstance(data, bytes):
            return data.decode("utf-8")
        else:
            print("Unexpected response type")
            return None
    except Exception as e:
        print(f"Error sending text message: {e}")
        return None
    
    
    
def congratulatin_msg_when_doctor_register_aisensy(patient_mobile_number):
    destination = str(patient_mobile_number)
 
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "register_congratulation_doctor_msg",
        "destination": destination,
        "userName": "Digiquest Consultancy Services Private Limited",
        "templateParams": [
            "Digiquest Consultancy",
            "DigiQuest Consultancy",
        ],
    }

    url = 'https://backend.aisensy.com/campaign/t1/api/v2'
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as err:
        return {'error': 'HTTP error occurred', 'details': str(err)}
    
    except requests.exceptions.ConnectionError as err:
        return {'error': 'Connection error occurred', 'details': str(err)}