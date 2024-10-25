import http
import json
import requests
from twilio.rest import Client
from django.core.cache import cache
import random
import os
from django.core.mail import send_mail
from django.conf import settings
import uuid










def patient_appointment(mobile_no, doctor_name, booked_date, slot_time):
    account_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
         body=f" your appoinment successfully booked with Doctor {doctor_name} on {booked_date} {slot_time}",
        from_=os.environ.get('TWILIO_NUMBER'),
        to='+91'+str(mobile_no)
    )
    print(message.sid,)
    return

def doctor_appointment(mobile_no, patient_name, booked_date, slot_time):
    account_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"appoinment booked with {patient_name} on {booked_date} {slot_time}",
        from_=os.environ.get('TWILIO_NUMBER'),
        to='+91'+str(mobile_no)
    )
    print(message.sid,)
    return 

    
    
# def send_blocked_slot_notification(doctor_name, patient_name, booked_date, slot_time):
#     subject = 'Appointment Rescheduling Required'
#     message = (
#         f'Hi {patient_name},\n\n'
#         f'This is Niramaya Homoeopathy. We need to reschedule your appointment with Dr. {doctor_name} '
#         f'on {booked_date} at {slot_time} because the doctor is unavailable at that time. you can book your slot for next available slot'
#         f'Please call us at +919935266755 to book a new slot. Sorry for the inconvenience. Thanks!'
#     )
#     recipient_email = os.environ.get('RECIPIENT_EMAIL')  
#     send_mail(subject, message, None, [recipient_email])
    
def send_blocked_slot_notification(patient_mobile_number,doctor_name,patient_name,booked_date,slot_time,):
    account_sid = os.environ.get('ACCOUNT_SID')
    auth_token = os.environ.get('AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f'Hi {patient_name},\n\n'
        f'This is Niramaya Homoeopathy. We need to reschedule your appointment with Dr. {doctor_name} '
        f'on {booked_date} at {slot_time} because the doctor is unavailable at that time. you can book your slot for next available slot'
        f'Please call us at +919935266755 to book a new slot. Sorry for the inconvenience. Thanks!',
        from_=os.environ.get('TWILIO_NUMBER'),
        to='+91'+str(patient_mobile_number)
    )
    print(message.sid)


AISENSY_API_KEY = os.environ.get('AISENSY_API_KEY')
SENDER_WHATSAPP_NUMBER = os.environ.get('SENDER_WHATSAPP_NUMBER')
    
    
    
    
    
# ===============================cancel appointment message to patient=========================================== 
    
    
def appointment_cancel_message_to_doctor_msg91(doctor_name, booked_date, slot_time, patient_mobile_number, hospital_number):
    mobile_no = str(patient_mobile_number)
    date_time = f"{booked_date} at {slot_time}"
    full_mobile_number = f"91{mobile_no}"

    payload = {
        "template_id": "6707cb4fd6fc0537ab3a3744",
        "short_url": "0",
        "realTimeResponse": "1",
        "recipients": [
            {
                "mobiles": full_mobile_number,
                "var1": str(doctor_name),
                "var2": str(date_time),
                "var3": str(hospital_number)
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
        response = requests.post("https://control.msg91.com/api/v5/flow", headers=headers, data=json_payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error sending text message: {e}")
        return None



def send_whatsapp_cancel_message(patient_mobile_number, patient_name, hospital_name, doctor_name, booked_date, slot_time, hospital_number):
    destination = str(patient_mobile_number)
 
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "final_slot_cancel_notification_to_patient",
        "destination": destination,
        "userName": "Digiquest Consultancy Services Private Limited",
        "templateParams": [
            str(patient_name),
            str(hospital_name),
            str(doctor_name),
            str(booked_date),
            str(slot_time),
            str(hospital_number)
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
    
    except Exception as err:
        return {'error': 'Other error occurred', 'details': str(err)}



#=============================================appointment confirm message to doctor and patient========================================

#=========whatsapp====================
    
def send_whatsapp_booked_msg_doctor(patient_name, hospital_name, doctor_name, booked_date, slot_time, hospital_number):
    destination = str(hospital_number)
 
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "appointment_confirm_message_to_doctor",
        "destination": destination,
        "userName": "Digiquest Consultancy Services Private Limited",
        "templateParams": [
            str(doctor_name),
            str(patient_name),
            str(booked_date),
            str(slot_time),
            str(patient_name),
            str(booked_date),
            str(slot_time),
            str(hospital_name)
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
    
    except Exception as err:
        return {'error': 'Other error occurred', 'details': str(err)}
    
    
    

def send_whatsapp_booked_msg_to_patient(patient_mobile_number,patient_name, hospital_name, doctor_name, booked_date, slot_time, hospital_number):
    destination = str(patient_mobile_number)
 
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "appointment_confirm_message_to_patient",
        "destination": destination,
        "userName": "Digiquest Consultancy Services Private Limited",
        "templateParams": [
            str(patient_name),
            str(doctor_name),
            str(booked_date),
            str(slot_time),
            str(doctor_name),
            str(booked_date),
            str(slot_time),
            str(hospital_name),
            str(hospital_number),
            str(hospital_name)
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
    
    except Exception as err:
        return {'error': 'Other error occurred', 'details': str(err)}


#==========msg91===========================================

def appointment_confirm_message_to_doctor_msg91(patient_name,booked_date,slot_time,hospital_number):
    mobile_no = str(hospital_number)
    date_time = f"{booked_date} at {slot_time}"
    full_mobile_number = f"91{mobile_no}"

    payload = {
        "template_id": "670f5972d6fc051ab50e9ac2",
        "short_url": "0",
        "realTimeResponse": "1",
        "recipients": [
            {
                "mobiles": full_mobile_number,
                "var1": str(patient_name),
                "var2": str(date_time),
                "var3": str(hospital_number)
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
        response = requests.post("https://control.msg91.com/api/v5/flow", headers=headers, data=json_payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error sending text message: {e}")
        return None








def appointment_confirm_message_to_patient_msg91(doctor_name, booked_date, slot_time, patient_mobile_number,clinic_city,street_address,landmark,pin_code):
    mobile_no = str(patient_mobile_number)
    date_time = f"{booked_date}at {slot_time}"
    address = f"{street_address}, {landmark}, {clinic_city}, {pin_code}"
    full_mobile_number = f"91{mobile_no}"

    payload = {
        "template_id": "670d0d55d6fc0526840db442",
        "short_url": "0",
        "realTimeResponse": "1",
        "recipients": [
            {
                "mobiles": full_mobile_number,
                "var1": str(doctor_name),
                "var2": str(date_time),
                "var3": str(address)
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
        response = requests.post("https://control.msg91.com/api/v5/flow", headers=headers, data=json_payload)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error sending text message: {e}")
        return None



























#=====================send reminder message to doctor and patient with link using whatsapp ======================================================


def generate_meeting_link():
    # Generate a unique meeting link using Jitsi Meet
    room_name = f"meeting-{uuid.uuid4()}"
    meeting_link = f"https://meet.jit.si/{room_name}"
    
    return meeting_link  # Return only the generated meeting link

meeting_link = generate_meeting_link()


def send_reminder_to_patient(patient_mobile_number, patient_name, hospital_name, doctor_name, booked_date, slot_time, hospital_number):
    destination = str(patient_mobile_number)
    
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "reminder_patient_for_appointment",
        "destination": destination,
        "userName": "Digiquest Consultancy Services Private Limited",
        "templateParams": [
            str(patient_name),
            str(doctor_name),
            str(doctor_name),
            str(booked_date),
            str(slot_time),
            str(meeting_link),  # Pass the generated meeting link here
            str(hospital_number),
            str(hospital_name),
        ],
    }

    url = 'https://backend.aisensy.com/campaign/t1/api/v2'
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error if the request fails
        return response.json()  # Return the response from the API
    
    except requests.exceptions.HTTPError as err:
        return {'error': 'HTTP error occurred', 'details': str(err)}
    
    except requests.exceptions.ConnectionError as err:
        return {'error': 'Connection error occurred', 'details': str(err)}
    
    except Exception as err:
        return {'error': 'Other error occurred', 'details': str(err)}
    

    
    
def send_reminder_to_doctor(patient_mobile_number, patient_name, hospital_name, doctor_name, booked_date, slot_time, hospital_number):
    destination = str(hospital_number)

    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "reminder_doctor_for_appointment",
        "destination": destination,
        "userName": "Digiquest Consultancy Services Private Limited",
        "templateParams": [
            str(patient_name),
            str(doctor_name),
            str(doctor_name),
            str(booked_date),
            str(slot_time),
            str(meeting_link),  # Pass the generated meeting link here
            str(hospital_number),
            str(hospital_name),
        ],
    }

    url = 'https://backend.aisensy.com/campaign/t1/api/v2'
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an error if the request fails
        return response.json()  # Return the response from the API
    
    except requests.exceptions.HTTPError as err:
        return {'error': 'HTTP error occurred', 'details': str(err)}
    
    except requests.exceptions.ConnectionError as err:
        return {'error': 'Connection error occurred', 'details': str(err)}
    
    except Exception as err:
        return {'error': 'Other error occurred', 'details': str(err)}
    
    
    
    
    
