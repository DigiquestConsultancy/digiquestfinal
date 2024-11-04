import http
import json
import secrets
import string
import requests
from twilio.rest import Client
from django.core.cache import cache
import random
import os

AISENSY_API_KEY = os.getenv('AISENSY_API_KEY')     
    
    
# ===========================Register OTP for patient using twilio and aisensy============================


def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choice('0123456789') for _ in range(6))



def register_otp_to_patient(mobile_no, otp):
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


def send_register_otp_to_patient(mobile_number, otp):
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
    
    
    
    
    
# ======================================login otp for doctor  ============================================================================    
    
    
    
    
    
def login_otp_to_patient(mobile_no, otp):
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
    
    



def send_login_otp_to_patient(mobile_number, otp):
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
    
    
    
    
    
    
    
    

#=======================================Congratulation Message When Patient Register======================================================


def congratulation_msg_when_patient_register_msg91(patient_mobile_number):
    conn = http.client.HTTPSConnection("control.msg91.com")
    
    mobile_no = str(patient_mobile_number) 
    full_mobile_number = f"91{mobile_no}"
    
    payload = {
        "template_id": "670cccbed6fc0518c67e0633",  
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
    
    
    
    
def congratulation_msg_when_patient_register_aisensy(patient_mobile_number):
    destination = str(patient_mobile_number)
 
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "congratulation_msg_when_patient_register",
        "destination": destination,
        "userName": "Digiquest Consultancy Services Private Limited",
        "templateParams": [
            "DigiQuest Consultancy",
            "DigiQuest Consultancy"
        ],
    }

    url = 'https://backend.aisensy.com/campaign/t1/api/v2'
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an error for HTTP errors
        
        if response.json().get('status') == 'success':
            return {'message': 'Message sent successfully!'}
        else:
            return {'error': 'Message sending failed', 'details': response.json()}

    except requests.exceptions.HTTPError as err:
        return {'error': 'HTTP error occurred', 'details': str(err)}
    
    except requests.exceptions.ConnectionError as err:
        return {'error': 'Connection error occurred', 'details': str(err)}
    
    
    
    
    
    
    
#=======================================Congratulation Message with password When Patient Register======================================================


def generate_strong_password_patient(length=8):
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = '123456789'
    special = '@!#'
    
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase), 
        secrets.choice(digits),    
        secrets.choice(special)    
    ]
    
    allowed_characters = lowercase + uppercase + digits + special
    password += [secrets.choice(allowed_characters) for _ in range(length - 4)]
    
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)












def congratulation_msg_when_patient_register_msg91(patient_mobile_number, strong_password):
    conn = http.client.HTTPSConnection("control.msg91.com")
    
    mobile_no = str(patient_mobile_number) 
    full_mobile_number = f"91{mobile_no}"
    
    payload = {
        "template_id": "670cccbed6fc0518c67e0633",  
        "short_url": "0",  
        "realTimeResponse": "1",  
        "recipients": [
            {
                "mobiles": full_mobile_number,
                "var1": mobile_no,
                "var2": strong_password
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
    