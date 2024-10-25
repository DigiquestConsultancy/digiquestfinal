import http
import json
import os
import random
import requests
import secrets
import string






AISENSY_API_KEY = os.environ.get('AISENSY_API_KEY')




# ===========================Register OTP for reception using MSG91 and aisensy============================


def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join(random.choice('0123456789') for _ in range(6))



def register_otp_for_reception(mobile_no, otp):
    conn = http.client.HTTPSConnection("control.msg91.com")
    
    mobile_no = str(mobile_no)  
    otp = str(otp)              
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


def send_register_otp_to_reception(mobile_number, otp):
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














def generate_strong_password(length=8):
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


def reception_register_msg91(reception_mobile_number,strong_password):
    conn = http.client.HTTPSConnection("control.msg91.com")
    
    mobile_no = str(reception_mobile_number)  # Ensure mobile_no is a string    
    password = str(strong_password)              # Ensure otp is a string
    full_mobile_number = f"91{mobile_no}"
    
    payload = {
        "template_id": "670cb87dd6fc0561243730b3",  
        "short_url": "0",  
        "realTimeResponse": "1",  
        "recipients": [
            {
                "mobiles": full_mobile_number,
                "var1": mobile_no,
                "var2": password
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
    




def clinic_register_aisensy(reception_mobile_number, strong_password):
    destination = str(reception_mobile_number)
    password = str(strong_password)

    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "registration_message _to_reception_clinic",
        "destination": destination,
        "userName": "Digiquest Consultancy Services Private Limited",
        "templateParams": [
            destination,
            password,
            "techdcs.com"
        ],
        "source": "new-landing-page form",
        "media": {},
        "buttons": [],
        "carouselCards": [],
        "location": {},
        "paramsFallbackValue": {
            "FirstName": "user"
        }
        }

    url = 'https://backend.aisensy.com/campaign/t1/api/v2'

    try:
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f'HTTP error occurred: {err}')
        return None
    except requests.exceptions.ConnectionError as err:
        print(f'Connection error occurred: {err}')
        return None
    except Exception as err:
        print(f'Other error occurred: {err}')
        return None
