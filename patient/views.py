import datetime
import mimetypes
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
import os
import random
from datetime import datetime, timedelta
import socket
from django.core.cache import cache
# from django.contrib.gis.geoip2 import GeoIP2
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
import jwt
from rest_framework.views import APIView
from rest_framework.response import Response
import urllib3
from digiquest import settings
from clinic.models import ClinicDetails
from digiadmin.models import hash_value
from doctor.models import Address, DoctorDetail, DoctorRegister, PersonalsDetails, Qualification, SymptomsDetail
from reception.models import ReceptionDetails
from doctorappointment.serializers import BookedAppointmentSerializer
from doctorappointment.models import Appointmentslots
from .utils import generate_otp,  login_otp_to_patient,  register_otp_to_patient, send_login_otp_to_patient, send_register_otp_to_patient
from .serializers import  PatientDetailSerializer, MyAppointmentSerializer, PatientDetailSerializerPost, PatientDocumentByIdSerializer, PatientDocumentSearchSerializer ,PatientDocumentSerializer, PatientDocumentSerializermobile, PatientFeedbackSerializer, PatientPrescriptionFileSerializer, PatientPrescriptionSerializer, PatientRecordSerializer, PatientRegisterSerializer, PatientVarryDetailsSerializer, PatientViewDocument
from .models import PatientDetails, PatientDocument, PatientDocumentById, PatientPrescription, PatientPrescriptionFile,  PatientRecord, PatientRegister, PatientVarryDetails
from rest_framework import status
import re
import ipinfo
from django.db.models import Q

from rest_framework_simplejwt.tokens import RefreshToken
 

import logging
error_patient = logging.getLogger('error_patient')
info_patient = logging.getLogger('info_patient')
warning_patient = logging.getLogger('warning_patient')

class PatientVerification(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
 
        if not mobile_number:
            return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r"^\d{10}$", mobile_number):
            return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
        if PatientRegister.objects.filter(mobile_number=mobile_number).exists():
 
            try:
                cache.set("Patient" + str(mobile_number),mobile_number, timeout=60)
    
                otp = generate_otp()
                register_otp_to_patient(mobile_number, otp)
                send_register_otp_to_patient(mobile_number, otp)
                cache.set(mobile_number, otp, timeout=300)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
            return Response({"success": "OTP generated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Mobile number is not registered"}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        otp = request.data.get("otp")
 
        if not mobile_number or not otp:
            return Response({"error": "Mobile number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r"^\d{10}$", mobile_number):
            return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
 
   
        if not PatientRegister.objects.filter(mobile_number=mobile_number).exists():
            return Response({"error": "Mobile number is not registered. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
 
        cached_otp = cache.get(mobile_number)
        if cached_otp is None:
            return Response({"error": "Session expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
        if otp != cached_otp:
            return Response({"error": "Incorrect OTP. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
 
        return Response({"success": "Mobile number verify successfully!"}, status=status.HTTP_201_CREATED)
    

class PatientRegisterApi(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
        password = request.query_params.get("password")
        if not mobile_number or not password:
            error_patient.error("Mobile number and password are required")
            return Response({"error": "Mobile number and password are required"}, status=status.HTTP_400_BAD_REQUEST)
 
        if not re.match(r"^\d{10}$", mobile_number):
            error_patient.error(f"Invalid mobile number: {mobile_number}")
            return Response({"error": "Please enter a valid 10-digit mobile number."}, status=status.HTTP_400_BAD_REQUEST)
 
 
        if PatientRegister.objects.filter(mobile_number=mobile_number).exists():
            error_patient.error(
                f"Mobile number is already registered: {mobile_number}")
            return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)
        password_regex = r"^(?=.*[!@#$%^&*])[A-Z][a-zA-Z0-9!@#$%^&*]{7,15}$"
        if not re.match(password_regex, password):
            error_patient.error(f"Weak password: {password}")
            return Response({
                "error": "Password must start with an uppercase letter, be 8-16 characters long, and include at least one digit and one special character."
            }, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            hashed_password = hash_value(password)
            cache.set(f"Patient_{mobile_number}_password",hashed_password, timeout=300)
            
            
            # otp = ''.join(random.choices('0123456789', k=6))
            otp = generate_otp()
            register_otp_to_patient(mobile_number, otp)
            send_register_otp_to_patient(mobile_number, otp)
            info_patient.info(f"OTP generated for mobile number {mobile_number}: {otp}")
            cache.set(f"Patient_{mobile_number}_otp", otp,timeout=300)  
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        return Response({"success": "OTP generated successfully", "otp": otp}, status=status.HTTP_200_OK)
 
 
    def post(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        otp = request.data.get("otp")
        password = cache.get(f"Patient_{mobile_number}_password")
 
 
        if not mobile_number or not otp:
            return Response({"error": "Mobile number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
 
        cached_otp = cache.get(f"Patient_{mobile_number}_otp")
        if not cached_otp:
            return Response({"error": "OTP has expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
 
        if otp != cached_otp:
            return Response({"error": "Invalid OTP. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
 
        patient_register_serializer = PatientRegisterSerializer(data={
            'mobile_number': mobile_number,
            'password': password}
        )
 
        if patient_register_serializer.is_valid():
            patient_register_serializer.save()
            info_patient.info(
                f"Patient registered successfully with mobile number: {mobile_number}")
            return Response({"success": "You are successfully registered!"}, status=status.HTTP_200_OK)
        else:
            return Response(patient_register_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientLoginApiView(APIView):
    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            password = request.data.get("password")
 
            if not mobile_number or not password:
                return Response({"error": "Mobile number and password are required"}, status=status.HTTP_400_BAD_REQUEST)
 
            if not re.match(r"^\d{10}$", mobile_number):
                return Response({"error": "Please enter a valid 10-digit mobile number."}, status=status.HTTP_400_BAD_REQUEST)
 
            try:
                user = PatientRegister.objects.get(mobile_number=mobile_number)
            except PatientRegister.DoesNotExist:
                return Response({"error": "Incorrect mobile number and password"}, status=status.HTTP_404_NOT_FOUND)
 
            if hash_value(password) != user.password:
                return Response({"error": "Incorrect mobile number and password"}, status=status.HTTP_400_BAD_REQUEST)
            user_id = user.pk
            tokens = self.generate_tokens(mobile_number, user_id)
 
            info_patient.info(
                "Login successful for mobile number: %s", mobile_number)
 
            return Response({
                'success': "Login successful!",
                'user_type': 'patient',
                **tokens
            }, status=status.HTTP_200_OK)
 
        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            error_patient.error(error_message)
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
    def generate_tokens(self, mobile_number, user_id):
        refresh = RefreshToken()
        refresh['patient_id'] = user_id
        refresh['mobile_number'] = mobile_number
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
       
 
class ForgetPassword(APIView):
    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")
 
            if not mobile_number:
                error_patient.error("Mobile number is required")
                return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
 
            if not re.match(r"^\d{10}$", mobile_number):
                error_patient.error(
                    "Invalid mobile number format: %s", mobile_number)
                return Response({"error": "Please enter a valid 10-digit mobile number."}, status=status.HTTP_400_BAD_REQUEST)
 
            if new_password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
 
            try:
                login_instance = PatientRegister.objects.get(
                    mobile_number=mobile_number)
            except PatientRegister.DoesNotExist:
                return Response({"error": "Mobile number is not registered"}, status=status.HTTP_404_NOT_FOUND)
 
            hashed_password = hash_value(new_password)
            login_instance.password = hashed_password
            login_instance.save()
 
            return Response({"success": "Password has been changed successfully"}, status=status.HTTP_200_OK)
 
        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            error_patient.error(error_message)
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    
class PatientLoginApi(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
        if not mobile_number:
            error_patient.error({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r"^\d{10}$", mobile_number):
            return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
        if not PatientRegister.objects.filter(mobile_number=mobile_number).exists():
            return Response({"error": "Mobile number is not registered. Please register first."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # otp = ''.join(random.choices('0123456789', k=6))
            otp = generate_otp() 
            login_otp_to_patient(mobile_number, otp)
            send_login_otp_to_patient(mobile_number, otp)
            cache.set(mobile_number, otp, timeout=300)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"success": "OTP generated successfully"}, status=status.HTTP_200_OK)


    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            otp_entered = request.data.get("otp")
            if not mobile_number or not otp_entered:
                error_patient.error("Mobile number and OTP are required")
                return Response({"error": "Mobile number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
            cached_otp = cache.get(mobile_number)
            if not cached_otp:
                error_patient.error(
                    "OTP has expired or mobile number is not registered: %s", mobile_number)
                return Response({"error": "OTP has expired or mobile number is not registered"}, status=status.HTTP_400_BAD_REQUEST)
            if otp_entered != cached_otp:
                error_patient.error(
                    "Incorrect OTP entered for mobile number: %s", mobile_number)
                return Response({"error": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)
            user = PatientRegister.objects.get(mobile_number=mobile_number)
            user_id = user.pk
            tokens = self.generate_tokens(mobile_number, user_id)
            info_patient.info(
                "Login successful for mobile number: %s", mobile_number)
            return Response({
                'success': "Login successful!",
                'user_type': 'patient',
                **tokens
            }, status=status.HTTP_201_CREATED)
        except PatientRegister.DoesNotExist:
            error_patient.error(
                "User not found for mobile number: %s", mobile_number)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            error_patient.error(error_message)
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def generate_tokens(self, mobile_number, user_id):
        refresh = RefreshToken()
        refresh['patient_id'] = user_id
        refresh['mobile_number'] = mobile_number
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
class PatientDetailApi(APIView):
    def get(self, request, format=None):
        try:
            mobile_number = request.query_params.get('mobile_number')
            patient_details = PatientDetails.objects.prefetch_related('patient').filter(patient__mobile_number=mobile_number)
            serializer = PatientDetailSerializer(patient_details, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, *args, **kwargs):
        try:
            mobile_number = request.data.get("mobile_number")
            if not mobile_number:
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST) 
            existing_user_detail = PatientDetails.objects.filter(patient__mobile_number=mobile_number).first()
            if existing_user_detail:
                return Response({"error": "User details already exist for this mobile number"}, status=status.HTTP_400_BAD_REQUEST)
            patient_register = PatientRegister.objects.get(mobile_number=mobile_number)
            mutable_data = request.data.copy()
            mutable_data["patient"] = patient_register.pk
            patient_serializer = PatientDetailSerializerPost(data=mutable_data)
            if patient_serializer.is_valid():
                patient_serializer.save()
                return Response(patient_serializer.data, status=status.HTTP_201_CREATED)
            return Response(patient_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, format=None):
        mobile_number = request.data.get('mobile_number')  
        if not mobile_number:
            return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST) 
        try:
            user_details = PatientDetails.objects.get(patient__mobile_number=mobile_number)
        except Exception as e:
            return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PatientDetailSerializer(user_details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'User Details Updated'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, format=None):
        mobile_number = request.data.get('mobile_number')
        if not mobile_number:
            return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_details = PatientDetails.objects.get(patient__mobile_number=mobile_number)
        except Exception as e:
            return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)        
        serializer = PatientDetailSerializer(user_details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'User Details Updated'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetPatientDetailsUsingID(APIView):
    def get(self, request, format=None):
        try:
            patient_id = request.query_params.get('patient_id')
            patient_details = PatientDetails.objects.prefetch_related('patient').filter(id=patient_id)
            serializer = PatientDetailSerializer(patient_details, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        


# class PatientCity(APIView):
#     def get(self, request, format=None):
#         try:
#             ipv6_address = request.META.get('HTTP_X_FORWARDED_FOR', None)
#             if ipv6_address:
#                 for address in ipv6_address.split(','):
#                     if ':' in address:
#                         ipv6_address = address.strip()
#                         break
#             if not ipv6_address:
#                 s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
#                 s.connect(("ipv6.google.com", 80)) 
#                 ipv6_address = s.getsockname()[0]
#                 s.close()
#             access_token = '8406af336a5de0'  
#             handler = ipinfo.getHandler(access_token)
#             details = handler.getDetails(ipv6_address)
#             city = details.city
#             country = details.country_name
#             time_zone = details.timezone
#             state = details.region
#             return Response({'city': city, 'state': state, 'country': country, 'time_zone': time_zone})
#         except Exception as e:
#             return Response({"error": str(e)})



class PatientCity(APIView):
    def get(self, request, format=None):
        try:
            # Get the client's IPv6 address
            ipv6_address = request.META.get('HTTP_X_FORWARDED_FOR', None)
            if ipv6_address:
                for address in ipv6_address.split(','):
                    if ':' in address:
                        ipv6_address = address.strip()
                        break

            if not ipv6_address:
                s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                s.connect(("ipv6.google.com", 80))
                ipv6_address = s.getsockname()[0]
                s.close()

            access_token = '8406af336a5de0'
            handler = ipinfo.getHandler(access_token)
            details = handler.getDetails(ipv6_address)

            # Extract location details
            city = details.city
            country = details.country_name
            state = details.region
            time_zone = details.timezone



            addresses = Address.objects.filter(
                (Q(city=city) & Q(state=state)) |
                (Q(city=city) & Q(country=country)) |
                (Q(state=state) & Q(country=country))
            )

            doctors = DoctorRegister.objects.filter(address__in=addresses)

            doctor_list = []

            for doctor in doctors:
                personal_details = PersonalsDetails.objects.filter(doctor=doctor).first()
                qualifications = Qualification.objects.filter(doctor=doctor, is_selected=True).values_list('qualification', flat=True)

                if personal_details:
                    doctor_info = {
                        'name': personal_details.name,
                        'specialization': personal_details.specialization,
                        'email': personal_details.email,
                        'profile_pic': personal_details.profile_pic.url if personal_details.profile_pic else None,
                        'experience': personal_details.experience,
                        'qualifications': list(qualifications),
                    }
                    doctor_list.append(doctor_info)

            limited_doctor_list = doctor_list[:5]

            return Response({
                'city': city,
                'state': state,
                'country': country,
                'time_zone': time_zone,
                'doctors': limited_doctor_list
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)


























class PatientDocumentUpload(APIView):
    def get(self, request, format=None):
        try:
            mobile_number = request.query_params.get('mobile_number')
            if not mobile_number:
                return Response({"error": "mobile_number is required"}, status=status.HTTP_400_BAD_REQUEST)
            patient_register = PatientRegister.objects.filter(mobile_number=mobile_number).first()
            if not patient_register:
                error_patient.error("Patient with mobile number %s does not exist", mobile_number)
                return Response({"error": "Patient with this mobile number does not exist"}, status=status.HTTP_404_NOT_FOUND)
            patient = PatientDetails.objects.filter(patient=patient_register).first()
            if not patient:
                error_patient.error("Patient details not found for mobile number %s", mobile_number)
                return Response({"error": "Patient details not found for this mobile number"}, status=status.HTTP_404_NOT_FOUND)
            documents = PatientDocument.objects.filter(patient=patient)
            if not documents:
                return Response({"message": "You have no uploaded documents. Upload your document here."})
            serializer = PatientDocumentSerializermobile(documents, many=True)
            return Response(serializer.data)
        except Exception as e:
            error_patient.error("An error occurred while processing GET request: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    def post(self, request, format=None):
        try:
            mobile_number = request.data.get('mobile_number')
            document_name = request.data.get('document_name')
            document_file = request.data.get('document_file')
            document_date = request.data.get('document_date')
            patient_name = request.data.get('patient_name')
            document_type=request.data.get('document_type')
            if not mobile_number or not document_name or not document_file or not document_type:
                error_patient.error("Incomplete data provided for POST request: %s", request.data)
                return Response({"error": "mobile_number, document_name, document_file and document_type are required fields"}, status=status.HTTP_400_BAD_REQUEST)
            patient_register = PatientRegister.objects.filter(mobile_number=mobile_number).first()
            if not patient_register:
                error_patient.error("Patient with mobile number %s does not exist", mobile_number)
                return Response({"error": "Patient with this mobile number does not exist"}, status=status.HTTP_404_NOT_FOUND)

            patient = PatientDetails.objects.filter(patient=patient_register).first()
            if not patient:
                error_patient.error("Patient details not found for mobile number %s", mobile_number)
                return Response({"error": "Patient details not found for this mobile number"}, status=status.HTTP_404_NOT_FOUND)
            document_data = {
                'patient': patient.id,
                'document_name': document_name,
                'document_file': document_file,
                'document_date': document_date,
                'patient_name': patient_name,
                'document_type': document_type
            }
            serializer = PatientDocumentSerializer(data=document_data)
            if serializer.is_valid():
                serializer.save()
                info_patient.info("Document uploaded successfully for patient %s", patient.name)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                error_patient.error("Validation error occurred while processing POST request: %s", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_patient.error("An error occurred while processing POST request: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, format=None):
        try:
            mobile_number = request.data.get('mobile_number')
            document_id = request.data.get('document_id')  # Assuming this is how you identify the document to update
            if not mobile_number or not document_id:
                return Response({"error": "mobile_number and document_id are required fields"}, status=status.HTTP_400_BAD_REQUEST)

            patient_register = PatientRegister.objects.filter(mobile_number=mobile_number).first()
            if not patient_register:
                return Response({"error": "Patient with this mobile number does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            patient = PatientDetails.objects.filter(patient=patient_register).first()
            if not patient:
                return Response({"error": "Patient details not found for this mobile number"}, status=status.HTTP_404_NOT_FOUND)

            document_instance = PatientDocument.objects.filter(id=document_id, patient=patient).first()
            if not document_instance:
                return Response({"error": "Document not found for this patient"}, status=status.HTTP_404_NOT_FOUND)

            serializer = PatientDocumentSerializer(instance=document_instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, format=None):
        try:
            mobile_number = request.query_params.get('mobile_number')
            document_id = request.query_params.get('document_id')
            
            if not mobile_number or not document_id:
                return Response({"error": "mobile_number and document_id are required fields"}, status=status.HTTP_400_BAD_REQUEST)

            patient_register = PatientRegister.objects.filter(mobile_number=mobile_number).first()
            if not patient_register:
                return Response({"error": "Patient with this mobile number does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            patient = PatientDetails.objects.filter(patient=patient_register).first()
            if not patient:
                return Response({"error": "Patient details not found for this mobile number"}, status=status.HTTP_404_NOT_FOUND)

            document_instance = PatientDocument.objects.filter(id=document_id, patient=patient).first()
            if not document_instance:
                return Response({"error": "Document not found for this patient"}, status=status.HTTP_404_NOT_FOUND)

            document_instance.delete()
            return Response({"message": "Document deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class PatientDocumentUsingAppointmentID(APIView):
    
#     def get(self, request, *args, **kwargs):
#         try:
#             appointment_id = request.query_params.get('appointment')
#             if not appointment_id or not Appointmentslots.objects.filter(id=appointment_id).exists():
#                 return Response({"error": "Valid appointment ID is required."}, status=status.HTTP_400_BAD_REQUEST)
#             documents = PatientDocumentById.objects.filter(appointment_id=appointment_id)

#             data = [
#                 {
#                     "id":doc.id,
#                     "document_name": doc.document_name,
#                     "document_file": doc.document_file.url if doc.document_file else None,
#                     "patient_name": doc.patient_name,
#                     "document_date": doc.document_date,
#                     "uploaded_by": doc.uploaded_by,
#                     "document_type": doc.document_type,

#                 }
#                 for doc in documents
#             ]

#             return Response({"documents": data}, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PatientDocumentUsingAppointmentID(APIView):
    
    def get(self, request, *args, **kwargs):
        try:
            document_date = request.query_params.get('document_date')
            appointment_id = request.query_params.get('appointment')

            if not appointment_id or not Appointmentslots.objects.filter(id=appointment_id).exists():
                return Response({"error": "Valid appointment ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            documents = PatientDocumentById.objects.filter(appointment_id=appointment_id)

            if document_date:
                documents = documents.filter(document_date=document_date)


            if not documents.exists():
                return Response({"error": "No documents found matching the criteria."}, status=status.HTTP_404_NOT_FOUND)

            serializer = PatientDocumentSerializer(documents, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            appointment_id = request.data.get('appointment')
            user_type = request.data.get('user_type')
            user_id = request.data.get('user_id')
            patient_id=request.data.get('patient_id')


            if not appointment_id or not Appointmentslots.objects.filter(id=appointment_id).exists():
                return Response({"error": "Valid appointment ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            if user_type == 'clinic':
                clinic = get_object_or_404(ClinicDetails, clinic_id=user_id)
                uploaded_by = f"{clinic.name} (clinic)"
            elif user_type == 'doctor':
                doctor = get_object_or_404(PersonalsDetails, doctor_id=user_id)
                uploaded_by = f"{doctor.name} (doctor)"
            elif user_type == 'reception':
                reception = get_object_or_404(ReceptionDetails, reception_id=user_id)
                uploaded_by = f"{reception.name} (reception)"
            else:
                patient= get_object_or_404(PatientVarryDetails, id=patient_id)
                uploaded_by = f"{patient.name} (patient)"

            document_name = request.data.get('document_name')
            document_file = request.FILES.get('document_file')
            patient_name = request.data.get('patient_name')
            document_date = request.data.get('document_date')
            document_type = request.data.get('document_type')

            if not all([document_name, patient_name, document_date, document_type]):
                return Response({"error": "All required fields must be provided."}, status=status.HTTP_400_BAD_REQUEST)

            patient_document = PatientDocumentById.objects.create(
                appointment_id=appointment_id,
                document_name=document_name,
                document_file=document_file,
                patient_name=patient_name,
                document_date=document_date,
                uploaded_by=uploaded_by,
                document_type=document_type
            )
            print(patient_document)
            return Response({"success": "Document uploaded successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def patch(self, request, *args, **kwargs):
        try:
            document_id = request.data.get('document_id')
            if not document_id:
                return Response({"error": "Document ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the document or return a 404 if not found
            document = PatientDocumentById.objects.filter(id=document_id).first()
            if not document:
                return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

            document_name = request.data.get('document_name')
            document_file = request.FILES.get('document_file')
            patient_name = request.data.get('patient_name')
            document_date = request.data.get('document_date')
            document_type = request.data.get('document_type')

            if document_name is not None:
                document.document_name = document_name
            if document_file is not None:
                document.document_file = document_file
            if patient_name is not None:
                document.patient_name = patient_name
            if document_date is not None:
                document.document_date = document_date
            if document_type is not None:
                document.document_type = document_type

            document.save()
            serializer = PatientDocumentSerializer(document)
            return Response({"success": "Document updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            document_id = request.data.get('document_id')
            if not document_id:
                return Response({"error": "Document ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the document or return a 404 if not found
            document = PatientDocumentById.objects.filter(id=document_id).first()
            if not document:
                return Response({"error": "Document not found."}, status=status.HTTP_404_NOT_FOUND)

            document.delete()
            return Response({"success": "Document deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class ViewDocumentByAppointmentId(APIView):
    def get(self, request, format=None):
        try:
            document_id = request.query_params.get('document_id')

            if not document_id:
                return Response({"error": "Document ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            document = PatientDocumentById.objects.filter(id=document_id).first()
            if not document:
                return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

            # Construct file path
            file_path = document.document_file.path
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'  # Fallback MIME type

            try:
                response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
                response['Content-Disposition'] = f'attachment; filename="{document.document_file.name}"'
                return response
            except FileNotFoundError:
                raise Http404("File not found")
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ViewDocument(APIView):
    def get(self, request, format=None):
        try:
            patient_id = request.query_params.get('patient_id')
            document_id = request.query_params.get('document_id')

            if not patient_id or not document_id:
                return Response({"error": "Patient ID and Document ID are required"}, status=status.HTTP_400_BAD_REQUEST)

            patient = PatientDetails.objects.filter(id=patient_id).first()
            if not patient:
                return Response({"error": "Patient with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)

            document = PatientDocument.objects.filter(id=document_id, patient=patient).first()
            if not document:
                return Response({"error": "Document not found for this patient"}, status=status.HTTP_404_NOT_FOUND)


            file_path = document.document_file.path
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'  # Fallback MIME type

            try:
                response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
                response['Content-Disposition'] = f'attachment; filename="{document.document_file.name}"'
                return response
            except FileNotFoundError:
                raise Http404("File not found")
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

       

class PatientDocumentSearch(APIView):
    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        query = request.query_params.get("query")

        if not query or not patient_id:
            return Response({"message": "Please provide both patient_id and a query to search for patient documents."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch patient_id from PatientDetails model
            patient_id = PatientDetails.objects.get(patient_id=patient_id).id
        except PatientDetails.DoesNotExist:
            return Response({"error": "Patient details not found for the specified patient ID."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Query PatientDocument based on patient_id and search query
            appointments = PatientDocument.objects.filter(patient_id=patient_id).filter(
                Q(document_date__icontains=query) |
                Q(document_name__icontains=query) |
                Q(document_type__icontains=query)
            )
        except PatientDocument.DoesNotExist:
            return Response({"error": "No documents found for the specified patient ID."}, status=status.HTTP_404_NOT_FOUND)

        if not appointments.exists():
            return Response({"error": "No documents found for the specified query."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientDocumentSearchSerializer(appointments, many=True)
        return Response(serializer.data)

    
    
class PatientPrescriptionApi(APIView):
    def get(self, request, format=None):
        patient_id = request.query_params.get('patient_id')
        appointment_id = request.query_params.get('appointment_id')

        try:
            if not patient_id or not appointment_id:
                return Response({'error': 'patient_id and appoinment_id are required'}, status=status.HTTP_400_BAD_REQUEST)

            patient=PatientVarryDetails.objects.get(patient_id__id=patient_id, appointment_id=appointment_id)
            patient_prescriptions = PatientPrescription.objects.filter(
                patient_id=patient.id,
                appointment_id=appointment_id
            )

            if not patient_prescriptions.exists():
                return Response({'error': 'No prescriptions found for the given patient_id and appoinment_id'}, status=status.HTTP_404_NOT_FOUND)

            serializer = PatientPrescriptionSerializer(
                patient_prescriptions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            error_patient.error(f"Error occurred in get request: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request, format=None):
        try:

            prescriptions = request.data
            if not isinstance(prescriptions, list):
                return Response({'error': 'Request data must be a list of prescriptions'}, status=status.HTTP_400_BAD_REQUEST)

            errors = []
            valid_prescriptions = []

            for prescription in prescriptions:
                patient_id = prescription.get('patient_id')
                time= prescription.get('time')
                medicine_name = prescription.get('medicine_name')
                comment = prescription.get('comment')
                description = prescription.get('description')
                appointment_id = prescription.get('appointment_id')

                if not patient_id or not medicine_name or not appointment_id:
                    errors.append({"error": "patient_id, medicine_name, time, and appointment_id are required fields"})
                    continue

                try:
                    patient_details = PatientVarryDetails.objects.get(patient_id=patient_id, appointment_id=appointment_id)
                except PatientVarryDetails.DoesNotExist:
                    errors.append({"error": f"Patient details not found for patient_id {patient_id} and appointment_id {appointment_id}"})
                    continue

                prescription_data = {
                    "patient": patient_details.id,
                    "patient_name": patient_details.name,
                    "medicine_name": medicine_name,
                    "description": description,
                    "time": time,
                    "comment": comment,
                    "appointment": appointment_id
                }

                serializer = PatientPrescriptionSerializer(data=prescription_data)
                if serializer.is_valid():
                    valid_prescriptions.append(serializer.validated_data)
                else:
                    errors.append({'error': 'Data is not valid', 'record_errors': serializer.errors})

            # Bulk create valid prescriptions
            if valid_prescriptions:
                PatientPrescription.objects.bulk_create([PatientPrescription(**prescription) for prescription in valid_prescriptions])

            # Prepare response
            if errors:
                response_data = {
                    "success": "Some records processed successfully",
                    "errors": errors
                }
                status_code = status.HTTP_400_BAD_REQUEST
            else:
                response_data = {
                    "success": "All records created successfully"
                }
                status_code = status.HTTP_201_CREATED

            return Response(response_data, status=status_code)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def put(self, request, format=None):
        try:
            patient_id = request.data.get('patient_id')
            prescription_id = request.data.get('prescription_id')
 
   
            if not prescription_id or not patient_id:
                return Response({"error": "prescription_id and patient_id are required"}, status=status.HTTP_400_BAD_REQUEST)
 
            try:
                prescription = PatientPrescription.objects.get(
                    id=prescription_id, patient_id=patient_id)
            except PatientPrescription.DoesNotExist:
                return Response({"error": "Prescription not found"}, status=status.HTTP_404_NOT_FOUND)
 
     
            serializer = PatientPrescriptionSerializer(
                prescription, data=request.data, partial=True)
 
         
            if serializer.is_valid():
                serializer.save()
                info_patient.info("Prescription updated successfully")
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
        except Exception as e:
            error_patient.error(f"Error occurred in put request: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, format=None):
        try:
   
            prescription_id = request.query_params.get('prescription_id')
            if not prescription_id:
                return Response({"error": "prescription_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
            try:
                prescription = PatientPrescription.objects.get(
                    id=prescription_id)
            except PatientPrescription.DoesNotExist:
                return Response({"error": "Prescription not found"}, status=status.HTTP_404_NOT_FOUND)
 
            prescription.delete()
            return Response({"message": "Prescription deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
 
        except Exception as e:
            error_patient.error(f"Error occurred in delete request: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
        
        

 
        
class PatientFeedbackApi(APIView):
    def post(self, request, format=None):
        serializer = PatientFeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Feedback submitted successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        print(request.data)
        return Response({"error": "data is not valid", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class PatientDetailByDoctor(APIView):

    def post(self, request, format=None):
        try:
            mobile_number = request.data.get('mobile_number')
            name = request.data.get('name')
            address = request.data.get('address')
            date_of_birth = request.data.get('date_of_birth')
            gender = request.data.get('gender')
            blood_group = request.data.get('blood_group')
            age = request.data.get('age')
            profile_pic = request.data.get('profile_pic')  

            if not (mobile_number and name and date_of_birth and gender and blood_group and address):
                return Response({'error': 'All required fields must be provided.'}, status=status.HTTP_400_BAD_REQUEST)
            patient_register_instance = PatientRegister.objects.filter(mobile_number=mobile_number).first()
            if patient_register_instance:
                return Response({'error': 'Patient with this mobile number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            patient_register_instance = PatientRegister.objects.create(mobile_number=mobile_number)

            patient_detail_data = {
                'patient': patient_register_instance.id,
                'name': name,
                'address': address,
                'date_of_birth': date_of_birth,
                'gender': gender,
                'blood_group': blood_group,
                'age': age,
                'profile_pic': profile_pic
            }

            patient_detail_serializer = PatientDetailSerializerPost(data=patient_detail_data)

            if patient_detail_serializer.is_valid():
                patient_detail_serializer.save()
                return Response({'success': 'Patient details created successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response(patient_detail_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SearchMyAppointments(APIView):
    def get(self, request):
        try:
            query = request.query_params.get("query", None)
            patient_id = request.query_params.get("patient_id", None)
            
            if not patient_id:
                return Response({"error": "Please provide a patient_id to retrieve appointments."}, status=status.HTTP_400_BAD_REQUEST)
            
            appointments = Appointmentslots.objects.filter(booked_by_id=patient_id)
            
            if query:
                filter_by_patient_name = Q(booked_by__name__icontains=query)
                filter_by_specialization = Q(doctor__specialization__icontains=query)
                filter_by_doctor_name = Q(doctor__name__icontains=query)
                filter_by_mobile_number = Q(doctor__doctor__mobile_number__icontains=query)
                
                appointments = appointments.filter(
                    filter_by_patient_name | filter_by_specialization | filter_by_doctor_name | filter_by_mobile_number
                )
            else:
                return Response({"success": "Please enter a query to search for appointments."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = MyAppointmentSerializer(appointments, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class PatientRecordView(APIView):
    def get(self, request, format=None):
        try:
            appointment_id = request.query_params.get('appointment_id')
            if not appointment_id:
                return Response({"error": "Appointment ID parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)
 
            appointment = Appointmentslots.objects.filter(
                id=appointment_id).first()
            if not appointment:
                return Response({"error": "Appointment not found "}, status=status.HTTP_404_NOT_FOUND)
           
            patient_records = PatientRecord.objects.filter(
                appointment=appointment)
            if not patient_records.exists():
                return Response({"error": "No patient vital found "}, status=status.HTTP_404_NOT_FOUND)
 
            serializer = PatientRecordSerializer(patient_records, many=True)
 
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            patient_id = request.data.get("patient_id")
            appointment_id = request.data.get("appointment_id")

            if not appointment_id or not patient_id:
                error_patient.error('Appointment ID and patient ID are missing in the request')
                return Response({'error': 'Appointment ID and patient ID are missing in the request'}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the PatientVarryDetails instance
            patient_varry_details = PatientVarryDetails.objects.filter(patient_id=patient_id).first()
            if not patient_varry_details:
                error_patient.error(f'Patient varry details not found for the given patient ID: {patient_id}')
                return Response({'error': 'Patient  not found '}, status=status.HTTP_400_BAD_REQUEST)

            appointment = Appointmentslots.objects.filter(id=appointment_id).first()
            if not appointment:
                error_patient.error(f'Appointment not found for the given ID: {appointment_id}')
                return Response({'error': 'Appointment not found '}, status=status.HTTP_400_BAD_REQUEST)

            existing_record = PatientRecord.objects.filter(patient=patient_varry_details, appointment=appointment)
            if existing_record.exists():
                error_patient.error('Patient vital already exists for this patient and appointment')
                return Response({'error': 'Patient vital already exists '}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'patient': patient_varry_details.id,
                'appointment': appointment_id,
                'blood_pressure': request.data.get('blood_pressure'),
                'body_temperature': request.data.get('body_temperature'),
                'pulse_rate': request.data.get('pulse_rate'),
                'heart_rate': request.data.get('heart_rate'),
                'oxygen_level': request.data.get('oxygen_level'),
                'sugar_level': request.data.get('sugar_level'),
                'weight': request.data.get('weight'),
                'height': request.data.get('height'),
                'bmi': request.data.get('bmi'),
            }
            serializer = PatientRecordSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data
                response_data['patient'] = patient_varry_details.id
                info_patient.info('Patient record created successfully', extra=response_data)
                return Response({"success": "Patient vital created successfully", "data": response_data}, status=status.HTTP_201_CREATED)
            else:
                error_patient.error('Data is not valid', extra=serializer.errors)
                return Response({"error": "Data is not valid", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            error_patient.exception('An error occurred while processing the request', exc_info=e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
 

 
    def put(self, request, format=None):
        try:
            patient_id = request.data.get("patient_id")
            appointment_id = request.data.get("appointment_id")

            if not patient_id or not appointment_id:
                error_patient.error('Appointment ID and patient ID are missing in the request')
                return Response({'error': 'Appointment ID and patient ID are missing in the request'}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the correct instance of PatientVarryDetails
            patient_varry_details = PatientVarryDetails.objects.filter(id=patient_id).first()
            if not patient_varry_details:
                error_patient.error(f'Patient varry details not found for the given patient ID: {patient_id}')
                return Response({'error': 'Patient register not found '}, status=status.HTTP_404_NOT_FOUND)

            appointment = Appointmentslots.objects.filter(id=appointment_id).first()
            if not appointment:
                error_patient.error(f'Appointment not found for the given ID: {appointment_id}')
                return Response({'error': 'Appointment not found for the given ID'}, status=status.HTTP_404_NOT_FOUND)

            patient_record = PatientRecord.objects.filter(
                patient=patient_varry_details, appointment=appointment).first()

            if not patient_record:
                error_patient.error('Patient record not found for the given patient ID and appointment')
                return Response({'error': 'Patient record not found for the given patient ID and appointment'}, status=status.HTTP_404_NOT_FOUND)

            serializer = PatientRecordSerializer(patient_record, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data
                response_data['patient'] = patient_varry_details.id
                info_patient.info('Patient record updated successfully', extra=response_data)
                return Response({"success": "Patient record updated successfully", "data": response_data}, status=status.HTTP_200_OK)
            else:
                error_patient.error('Data is not valid', extra=serializer.errors)
                return Response({"error": "Data is not valid", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_patient.exception('An error occurred while updating the patient record', exc_info=e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


    

class PatientNameByID(APIView):
    def get(self, request, format=None):
        try:
            appointment_id = request.query_params.get('appointment_id')
            if not appointment_id:
                return Response({"error": "appointment_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            patient_detail= PatientVarryDetails.objects.get(appointment_id=appointment_id)
            return Response({"name": patient_detail.name},status= status.HTTP_200_OK)
        except PatientVarryDetails.DoesNotExist:
            return Response({"error": "Patient Details not found."}, status= status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PatientDetailsAPIView(APIView):  
    def get(self, request, format=None):
        patient_id = request.query_params.get('patient_id')
        appointment_id = request.query_params.get('appointment_id')

        # If both parameters are missing, return a 400 Bad Request
        if not patient_id and not appointment_id:
            return Response({'error': 'At least one of patient_id or appointment_id query parameters is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if appointment_id:
                # If only appointment_id is provided, fetch details based on appointment_id
                appointment_detail = PatientVarryDetails.objects.filter(appointment_id=appointment_id).first()

                if not appointment_detail:
                    return Response({'error': 'No appointment found with the specified appointment id'}, status=status.HTTP_404_NOT_FOUND)

                serializer = PatientVarryDetailsSerializer(appointment_detail)
                return Response(serializer.data, status=status.HTTP_200_OK)

            if patient_id:
                # If only patient_id is provided, fetch booked appointment slots based on patient_id
                appointment_slots = Appointmentslots.objects.filter(booked_by__patient_id=patient_id)
                serializer = BookedAppointmentSerializer(appointment_slots, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        
        
    
    

    def post(self, request, format=None):
        serializer = PatientVarryDetailsSerializer(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data['mobile_number']

            try:
                patient_register = PatientRegister.objects.get(mobile_number=mobile_number)
            except PatientRegister.DoesNotExist:
                patient_register = PatientRegister.objects.create(mobile_number=mobile_number)
            patient_details_data = {
                'patient': patient_register, 
                'mobile_number': mobile_number,
                'name': serializer.validated_data['name'],
                'address': serializer.validated_data['address'],
                'date_of_birth': serializer.validated_data['date_of_birth'],
                'age': serializer.validated_data.get('age'),
                'gender': serializer.validated_data['gender'],
                'blood_group': serializer.validated_data['blood_group'],
                'profile_pic': serializer.validated_data.get('profile_pic'),
                'appointment': serializer.validated_data.get('appointment'),
                'email': serializer.validated_data.get('email'),
            }
            patient_details = PatientVarryDetails.objects.create(**patient_details_data)
            patient=PatientVarryDetailsSerializer(patient_details)

            return Response({'success': 'Patient details saved successfully', 'data':patient.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, format=None):
        try:
            patient_id = request.data.get('patient_id')
            appointment_id = request.data.get('appointment_id')
            
            if not (patient_id and appointment_id):
                return Response({'error': 'patient_id and appointment_id are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Fetch patient details
            patient_details = PatientVarryDetails.objects.select_related('patient').filter(appointment_id=appointment_id, patient_id=patient_id).first()
            
            if not patient_details:
                return Response({"error": "Patient details not found"}, status=status.HTTP_404_NOT_FOUND)
            
            # Serialize the patient details
            serializer = PatientVarryDetailsSerializer(patient_details, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'Patient details update successfully', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            
        
    def patch(self, request, format=None):
        patient_id = request.data.get('patient_id')
        appointment=request.data.get('appointment')
        if not patient_id or not appointment:
            return Response({'error': 'patient_id and appointment parameter is required in the request body'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            patient_details = PatientVarryDetails.objects.get(id=patient_id)
        except PatientVarryDetails.DoesNotExist:
            return Response({'error':'Patient details not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PatientVarryDetailsSerializer(patient_details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'sucess':'Slot Booking Confirm'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UploadPrescriptionFile(APIView):
    def get(self, request, format=None):
        appointment_id = request.query_params.get('appointment_id')
        
        if not appointment_id:
            return Response({'error': 'appointment_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        prescription_documents = PatientPrescriptionFile.objects.select_related('appointment').filter(appointment=appointment_id)

        
        if not prescription_documents.exists():
            return Response({'error': 'No prescription files found for the given parameters'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientPrescriptionFileSerializer(prescription_documents, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        serializer = PatientPrescriptionFileSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, *args, **kwargs):
        try:
            document_id=request.data.get('document_id')
            prescription_file = PatientPrescriptionFile.objects.get(id=document_id)
        except PatientPrescriptionFile.DoesNotExist:
            return Response({'error': 'Prescription file not found'}, status=status.HTTP_404_NOT_FOUND)
        
        prescription_file.delete()
        return Response({'success': 'Prescription file deleted successfully'}, status=status.HTTP_200_OK)
    
    
class UploadPrescriptionFileView(APIView):
    def get(self, request, format=None):
        try:
            document_id = request.query_params.get('document_id')
            if not document_id:
                return Response({"error": "Document ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            document = PatientPrescriptionFile.objects.filter(id=document_id).first()
            if not document:
                return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

            file_path = document.document_file.path
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'  # Fallback MIME type

            try:
                response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
                response['Content-Disposition'] = f'attachment; filename="{document.document_file.name}"'
                return response
            except FileNotFoundError:
                raise Http404("File not found")
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class PrintPatientReport(APIView):
    def get(self, request):
        appointment_id = request.query_params.get('appointment_id')
 
        try:
            appointment = Appointmentslots.objects.select_related('doctor').get(id=appointment_id)
            patient_details = PatientVarryDetails.objects.filter(appointment__id=appointment_id).first()
            if not patient_details:
                return HttpResponse("No matching patient found for this appointment.", status=404)
 
            records = PatientRecord.objects.filter(patient=patient_details)
            prescriptions = PatientPrescription.objects.filter(patient=patient_details)
            symptoms_details = SymptomsDetail.objects.filter(appointment__id=appointment_id)
            doctor_name = appointment.doctor.name  
 
            buffer = BytesIO()
            pdf = SimpleDocTemplate(buffer, pagesize=A4,
                                    rightMargin=50, leftMargin=50,
                                    topMargin=170, bottomMargin=30)
 
            elements = []
            style = getSampleStyleSheet()['Normal']
 
            bold_style = ParagraphStyle(name='Bold', fontSize=14, fontName='Helvetica-Bold')
            normal_style = ParagraphStyle(name='Normal', fontSize=12)
 
    
            patient_info_data = [
                ['Patient Name:', patient_details.name, 'Gender/Age:', f'{patient_details.get_gender_display()}/{patient_details.age}'],
                ['Contact:', patient_details.mobile_number, 'Doctor Name:', doctor_name],
                ['Address:', patient_details.address, '', '']  
            ]
 
 
            patient_info_table = Table(patient_info_data, colWidths=[2 * inch, 2.5 * inch, 1.5 * inch, 2 * inch])
            patient_info_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(patient_info_table)
            elements.append(Spacer(1, 12))
 
    
            if records.exists():
                records_data = [
                    ["Blood Pressure", "Body Temperature", "Sugar Level", "Pulse Rate", "Heart Rate", "Oxygen Level", "Weight", "Height", "BMI"]
                ] + [[
                    record.blood_pressure,
                    record.body_temperature,
                    record.sugar_level,
                    record.pulse_rate,
                    record.heart_rate,
                    record.oxygen_level,
                    record.weight,
                    record.height,
                    record.bmi
                ] for record in records]
                records_column_widths = [8 * inch / 9] * 9  
                self.add_table_to_pdf(elements, records_data, title="Patient Vitals", column_widths=records_column_widths, wrap_text=True)
 
            if symptoms_details.exists():
                symptoms_data = [
                    ["Symptoms", "Since", "Severity", "More Options"]
                ] + [[
                    symptom.symptoms.symptoms_name,
                    symptom.since or 'N/A',
                    symptom.get_severity_display() if symptom.severity else 'N/A',
                    symptom.more_options or 'N/A'
                ] for symptom in symptoms_details]
                self.add_table_to_pdf(elements, symptoms_data, title="Symptoms Details", column_widths=[8 * inch / 4] * 4, wrap_text=True)
 
    
            if prescriptions.exists():
                prescriptions_data = [
                    ["Medicine Name", "Comment", "Time", "Description"]
                ] + [[
                    prescription.medicine_name,
                    prescription.comment,
                    prescription.time,
                    prescription.description if prescription.description else 'N/A'
                ] for prescription in prescriptions]
                self.add_table_to_pdf(elements, prescriptions_data, title="Prescriptions", column_widths=[8 * inch / 4] * 4, wrap_text=True)
 
            pdf.build(elements)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="patient_report.pdf"'
            return response
 
        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}", status=500)
 
    def add_table_to_pdf(self, elements, data, title, column_widths=None, wrap_text=False):
        elements.append(Spacer(1, 12))
        title_style = getSampleStyleSheet()['Title']
        title_style.alignment = 0  
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))
 
        if column_widths is None:
            column_widths = [1.5 * inch] * len(data[0])
 
        table_data = []
        for row in data:
            new_row = []
            for value in row:
                if wrap_text:
                    new_row.append(Paragraph(str(value), getSampleStyleSheet()['Normal']))
                else:
                    new_row.append(str(value))
            table_data.append(new_row)
 
        table = Table(table_data, colWidths=column_widths)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),  
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),        
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),                  
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),    
            ('FONTSIZE', (0, 0), (-1, 0), 12),                    
            ('GRID', (0, 0), (-1, -1), 1, colors.black),          
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),                  
            ('FONTSIZE', (0, 1), (-1, -1), 10),                    
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),      
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ])
        table.setStyle(style)
        elements.append(table)
        elements.append(Spacer(1, 12))