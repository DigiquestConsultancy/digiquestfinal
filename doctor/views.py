from datetime import datetime, time, timedelta
import mimetypes
import random
import re
from django.core.cache import cache
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password

from clinic.models import ClinicRegister
from digiadmin.models import hash_value
from doctorappointment.models import Appointmentslots
from doctorappointment.serializers import DoctorSlotSerializer
from patient.models import PatientVarryDetails
from reception.models import ReceptionRegister
from .utils import generate_otp,  login_otp_to_doctor, register_otp_for_doctor,  send_login_otp_to_doctor, send_register_otp_to_doctor
from .serializers import   AddressSerializer, DetailSerializer, DoctorDetailSerializer, DoctorFeedbackSerializer, DoctorNameSpecializationSerializer, DoctorRegisterSerializer, DoctornameSerializer, OpdDaysSerializers, OpdTimeSerializer, PersonalsDetailsSerializer, QualificationSerializer, SearchDetailsSerializer, SymptomsDetailSerializer, SymptomsSerializer
from .models import    Address, DoctorRegister, DoctorDetail, Opd, OpdTime, PersonalsDetails, Qualification, Symptoms, SymptomsDetail
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q

import logging
error_doctor = logging.getLogger('error_doctor')
info_doctor = logging.getLogger('info_doctor')
warning_doctor= logging.getLogger('warning_doctor')


class UserVerification(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")

        # Validate mobile number
        if not mobile_number:
            return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r"^\d{10}$", mobile_number):
            return Response({"error": "Please enter a valid 10-digit mobile number."}, status=status.HTTP_400_BAD_REQUEST)

        user_type = None
        user_exists = False

        # Check in DoctorRegister
        if DoctorRegister.objects.filter(mobile_number=mobile_number).exists():
            user_type = 'doctor'
            user_exists = True

        # Check in ClinicRegister
        elif ClinicRegister.objects.filter(mobile_number=mobile_number).exists():
            user_type = 'clinic'
            user_exists = True

        # Check in ReceptionRegister
        elif ReceptionRegister.objects.filter(mobile_number=mobile_number).exists():
            user_type = 'reception'
            user_exists = True

        if user_exists and user_type:
            try:
                # Cache the user type and mobile number
                logging.info(f"Caching mobile number {mobile_number} with user type {user_type}")
                cache.set(user_type.capitalize() + str(mobile_number), mobile_number, timeout=300)  # Increased timeout to 300 seconds

                # Generate and cache the OTP
                otp = generate_otp()
            
                register_otp_for_doctor(mobile_number, otp)
                send_register_otp_to_doctor(mobile_number, otp)
                cache.set(mobile_number, otp, timeout=300)
                logging.info(f"OTP {otp} generated and cached for mobile number {mobile_number}")

            except Exception as e:
                logging.error(f"Error in caching: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "success": "OTP generated successfully",  
                "user_type": user_type
            }, status=status.HTTP_200_OK)

        else:
            logging.warning(f"Mobile number {mobile_number} not found in any user tables")
            return Response({"error": "Mobile number is not registered"}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            otp = request.data.get("otp")

            # Validate input
            if not mobile_number or not otp:
                return Response({"error": "Mobile number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

            if not re.match(r"^\d{10}$", mobile_number):
                return Response({"error": "Please enter a valid 10-digit mobile number."}, status=status.HTTP_400_BAD_REQUEST)

            # Check the cache for the user type and mobile number
            user_type = None
            for u_type in ['Doctor', 'Clinic', 'Reception']:
                cached_mobile_number = cache.get(u_type + str(mobile_number))
                if cached_mobile_number == mobile_number:
                    user_type = u_type.lower()
                    logging.info(f"Mobile number {mobile_number} found in cache with user type {user_type}")
                    break

            if not user_type:
                logging.warning(f"Mobile number {mobile_number} not registered or OTP session expired.")
                return Response({"error": "Mobile number is not registered or OTP session expired. Resend OTP."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the OTP is still valid
            cached_otp = cache.get(mobile_number)
            if cached_otp is None:
                logging.warning(f"Session expired for mobile number {mobile_number}.")
                return Response({"error": "Session expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)

            # Compare OTPs
            if otp != cached_otp:
                logging.error(f"Incorrect OTP for mobile number {mobile_number}.")
                return Response({"error": "Incorrect OTP. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

            # Successful OTP verification
            logging.info(f"OTP verified successfully for mobile number {mobile_number}")
            return Response({"success": "OTP Verified Successfully", "user_type": user_type}, status=status.HTTP_200_OK)

        except Exception as e:
            logging.error(f"Exception during OTP verification: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class DoctorRegisterApi(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
        password = request.query_params.get("password")
        
        try:
            # Validate mobile number and password presence
            if not mobile_number:
                error_doctor.error("Mobile number is required")
                return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not re.match(r"^\d{10}$", mobile_number):
                error_doctor.error("Please enter a valid 10-digit number.")
                return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
            
            if not password:
                error_doctor.error("Password is required")
                return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate password complexity
            password_regex = r"^(?=.*[!@#$%^&*])[A-Z][a-zA-Z0-9!@#$%^&*]{7,15}$"
            if not re.match(password_regex, password):
                return Response({
                    "error": "Password must start with an uppercase letter, be 8-16 characters long, and include at least one digit and one special character."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if the mobile number is already registered
            if DoctorRegister.objects.filter(mobile_number=mobile_number).exists():
                error_doctor.error(f"Mobile number {mobile_number} is already registered")
                return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)
            
            if ClinicRegister.objects.filter(mobile_number=mobile_number).exists():
                return Response({"error": 'You are already registered as a Clinic. Please try with another mobile number.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if ReceptionRegister.objects.filter(mobile_number=mobile_number).exists():
                return Response({"error": 'You are already registered as a Reception. Please try with another mobile number.'}, status=status.HTTP_400_BAD_REQUEST)
            

            otp = generate_otp()
            cache.set(mobile_number, otp, timeout=600)  
            
            register_otp_for_doctor(mobile_number, otp)
            send_register_otp_to_doctor(mobile_number, otp)
            
            info_doctor.info(f"OTP generated for mobile number {mobile_number}: {otp}")
            
            return Response({"success": "OTP generated successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            password = request.data.get("password")
            otp = request.data.get("otp")
            
            # Logging the incoming request data
            info_doctor.info(f"Mobile number: {mobile_number}, OTP: {otp}")
            
            # Validate presence of required fields
            if not mobile_number or not otp or not password:
                error_doctor.error("Mobile number, OTP, and password are required")
                return Response({"error": "Mobile number, OTP, and password are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate mobile number format
            if not re.match(r"^\d{10}$", mobile_number):
                error_doctor.error("Please enter a valid 10-digit number.")
                return Response({"error": "Please enter a valid 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if OTP is valid
            cached_otp = cache.get(mobile_number)
            if not cached_otp:
                error_doctor.error(f"OTP expired for mobile number {mobile_number}")
                return Response({"error": "Session expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
            
            if otp != cached_otp:
                error_doctor.error(f"Incorrect OTP for mobile number {mobile_number}")
                return Response({"error": "Incorrect OTP. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if mobile number is already registered
            if DoctorRegister.objects.filter(mobile_number=mobile_number).exists():
                error_doctor.error(f"Mobile number {mobile_number} is already registered")
                return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)
            
            hashed_password = hash_value(password)
            
            doctor_serializer = DoctorRegisterSerializer(data={
                "mobile_number": mobile_number,
                "password": hashed_password
            })
            
            if doctor_serializer.is_valid():
                doctor = doctor_serializer.save()

                qualifications_data = [
                    {'qualification': choice[0], 'is_selected': False, 'doctor': doctor.id}
                    for choice in Qualification.QUALIFICATION_CHOICES
                ]
                
                for qualification_data in qualifications_data:
                    qualification_serializer = QualificationSerializer(data=qualification_data)
                    if qualification_serializer.is_valid():
                        qualification_serializer.save()
                    else:
                        return Response(qualification_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                info_doctor.info(f"User with mobile number {mobile_number} successfully registered")
                return Response({
                    'success': "You are successfully registered!",
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(doctor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DoctorLoginThroughPassword(APIView):
    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            password = request.data.get("password")
            password_encrypt = hash_value(password)
            if not mobile_number or not password:
                return Response({"error": "Mobile number and password are required"}, status=status.HTTP_400_BAD_REQUEST)

            user = None
            user_type = None

            # Check for Doctor
            try:
                user = DoctorRegister.objects.get(mobile_number=mobile_number)
                user_type = 'doctor'
            except DoctorRegister.DoesNotExist:
                pass  # Continue to check other user types

            # Check for Clinic
            if user is None:
                try:
                    user = ClinicRegister.objects.get(mobile_number=mobile_number)
                    user_type = 'clinic'
                except ClinicRegister.DoesNotExist:
                    pass  # Continue to check other user types

            # Check for Reception
            if user is None:
                try:
                    user = ReceptionRegister.objects.get(mobile_number=mobile_number)
                    user_type = 'reception'
                except ReceptionRegister.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Password verification
            if user.password != password_encrypt:  # Use hashed password comparison in production
                return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)

            # Generate tokens
            user_id = user.pk
            tokens = self.generate_tokens(mobile_number, user_id, user_type)

            # Prepare response
            response_data = {
                'success': "Login successful!",
                'user_type': user_type,
                **tokens
            }

            # Include is_reset only for clinic and reception users
            if user_type in ['clinic', 'reception']:
                response_data['is_reset'] = user.is_reset

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_tokens(self, mobile_number, user_id, user_type):
        refresh = RefreshToken()
        refresh[user_type + '_id'] = user_id
        refresh['mobile_number'] = mobile_number
        refresh['user_type'] = user_type

        try:
            if user_type == 'doctor':
                doctor_user = DoctorRegister.objects.get(mobile_number=mobile_number)
                refresh['is_verified'] = doctor_user.is_verified
                refresh['is_active'] = doctor_user.is_active

            elif user_type == 'clinic':
                clinic_user = ClinicRegister.objects.get(mobile_number=mobile_number)
                refresh['doctor_id'] = clinic_user.doctor_id

            elif user_type == 'reception':
                reception_user = ReceptionRegister.objects.get(mobile_number=mobile_number)
                refresh['doctor_id'] = reception_user.doctor_id

        except Exception as e:
            return Response({"error": "Error retrieving user details for mobile number"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }




class ChangePassword(APIView):
    def validate_password(self, password):
        if len(password) < 8:
            return "Password must be at least 8 characters long."
        if not re.search(r'[A-Z]', password):  # At least one uppercase letter
            return "Password must include at least one uppercase letter."
        if not re.search(r'[a-z]', password):  # At least one lowercase letter
            return "Password must include at least one lowercase letter."
        if not re.search(r'[0-9]', password):  # At least one digit
            return "Password must include at least one digit."
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # At least one special character
            return "Password must include at least one special character."
        return None  # Valid password

    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")

            # Check for missing fields
            if not mobile_number or not new_password or not confirm_password:
                return Response({"error": "Mobile number, new password, and confirm password are required"},
                                status=status.HTTP_400_BAD_REQUEST)

            # Check for password match
            if new_password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate password strength
            password_error = self.validate_password(new_password)
            if password_error:
                return Response({"error": password_error}, status=status.HTTP_400_BAD_REQUEST)

            # Try to find the user in both models
            user = None
            user_type = None

            try:
                user = ClinicRegister.objects.get(mobile_number=mobile_number)
                user_type = 'clinic'
            except ClinicRegister.DoesNotExist:
                try:
                    user = ReceptionRegister.objects.get(mobile_number=mobile_number)
                    user_type = 'reception'
                except ReceptionRegister.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Update the user's password
            user.password = hash_value(new_password)  # Hash the new password before saving
            user.is_reset = True
            user.save()

            return Response({"success": "Password changed successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






class ForgetPassword(APIView):
    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            new_password = request.data.get("new_password")
            confirm_password = request.data.get("confirm_password")

            # Log received values for debugging
            print(f"Received mobile_number: {mobile_number}, new_password: {new_password}, confirm_password: {confirm_password}")

            # Check if the new password and confirm password match
            if new_password is None or confirm_password is None:
                return Response({"error": "New password and confirm password are required"}, status=status.HTTP_400_BAD_REQUEST)

            if new_password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
            
            if len(new_password) < 8:
                return Response({"error": "Password must be at least 8 characters long"}, status=status.HTTP_400_BAD_REQUEST)

            user = None
            user_type = None

            # Check for Doctor
            try:
                user = DoctorRegister.objects.get(mobile_number=mobile_number)
                user_type = 'doctor'
            except DoctorRegister.DoesNotExist:
                pass  # Continue to check other user types

            # Check for Clinic
            if user is None:
                try:
                    user = ClinicRegister.objects.get(mobile_number=mobile_number)
                    user_type = 'clinic'
                except ClinicRegister.DoesNotExist:
                    pass  # Continue to check other user types

            # Check for Reception
            if user is None:
                try:
                    user = ReceptionRegister.objects.get(mobile_number=mobile_number)
                    user_type = 'reception'
                except ReceptionRegister.DoesNotExist:
                    return Response({"error": "Mobile number is not registered"}, status=status.HTTP_404_NOT_FOUND)

            # Ensure the user object is valid before accessing its password
            if user is None:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            # Hash the new password before saving
            user.password = hash_value(new_password)  # Ensure this function can handle None values
            user.save()

            return Response({"success": "Password has been changed successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




   
class DoctorLoginApi(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
        
        try:
            if not mobile_number:
                error_doctor.error("Mobile number is required")
                return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not re.match(r"^\d{10}$", mobile_number):
                error_doctor.error("Please enter a 10-digit number.")
                return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
            
            user_type = None
            
            if DoctorRegister.objects.filter(mobile_number=mobile_number).exists():
                user_type = 'doctor'
            else:
                if ClinicRegister.objects.filter(mobile_number=mobile_number).exists():
                    user_type = 'clinic'
                else:
                    if ReceptionRegister.objects.filter(mobile_number=mobile_number).exists():
                        user_type = 'reception'
                    else:
                        error_doctor.error("Mobile number %s is not registered. Please register first.", mobile_number)
                        return Response({"error": "Mobile number is not registered. Please register first."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                otp = generate_otp()
                
                login_otp_to_doctor(mobile_number, otp)
                send_login_otp_to_doctor(mobile_number, otp)
                
                cache.set(mobile_number, otp, timeout=60)
                print(otp)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            info_doctor.info("OTP generated successfully %s", otp)
            return Response({"success": "OTP generated successfully",  "user_type": user_type}, status=status.HTTP_200_OK)
        
        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            error_doctor.error(error_message)
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            otp_entered = request.data.get("otp")

            if not mobile_number or not otp_entered:
                error_doctor.error("Mobile number and OTP are required")
                return Response({"error": "Mobile number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

            cached_otp = cache.get(mobile_number)
            if not cached_otp:
                error_doctor.error("OTP has expired or mobile number is not registered: %s", mobile_number)
                return Response({"error": "OTP has expired or mobile number is not registered"}, status=status.HTTP_400_BAD_REQUEST)

            if otp_entered != cached_otp:
                error_doctor.error("Incorrect OTP entered for mobile number: %s", mobile_number)
                return Response({"error": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)

            # Determine user type and retrieve user object
            user_type = None
            user = None
            # clinic = DoctorRegister.objects.get(mobile_number=mobile_number)
            # doctor_id= clinic.doctor_id

            if DoctorRegister.objects.filter(mobile_number=mobile_number).exists():
                user_type = 'doctor'
                user = DoctorRegister.objects.get(mobile_number=mobile_number)
            else:
                if ClinicRegister.objects.filter(mobile_number=mobile_number).exists():
                    user_type = 'clinic'
                    user = ClinicRegister.objects.get(mobile_number=mobile_number)
                else:
                    if ReceptionRegister.objects.filter(mobile_number=mobile_number).exists():
                        user_type = 'reception'
                        user = ReceptionRegister.objects.get(mobile_number=mobile_number)
                    else:
                        error_doctor.error("User not found for mobile number: %s", mobile_number)
                        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            user_id = user.pk
            tokens = self.generate_tokens(mobile_number, user_id, user_type)
            info_doctor.info("Login successful for mobile number: %s", mobile_number)
            return Response({
                'success': "Login successful!",
                'user_type': user_type,
                **tokens
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            error_doctor.error(error_message)
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def generate_tokens(self, mobile_number, user_id, user_type):
        refresh = RefreshToken()
 
        refresh[user_type + '_id'] = user_id
        refresh['mobile_number'] = mobile_number
        refresh['user_type'] = user_type
   
        if user_type == 'doctor':
            try:
                doctor_user = DoctorRegister.objects.get(
                    mobile_number=mobile_number)
                refresh['is_verified'] = doctor_user.is_verified
                refresh['is_active'] = doctor_user.is_active
            except DoctorRegister.DoesNotExist:
                error_doctor.error(
                    f"Doctor user not found for mobile number: {mobile_number}")
            except Exception as e:
                error_doctor.error(f"Error retrieving doctor user for mobile number {mobile_number}: {str(e)}")
   
        elif user_type == 'clinic':
            try:
                clinic_user = ClinicRegister.objects.get(
                    mobile_number=mobile_number)
                refresh['doctor_id'] = clinic_user.doctor_id
            except ClinicRegister.DoesNotExist:
                error_doctor.error(
                    f"Clinic user not found for mobile number: {mobile_number}")
            except Exception as e:
                error_doctor.error(f"Error retrieving clinic user for mobile number {mobile_number}: {str(e)}")
   
        elif user_type == 'reception':
            try:
                reception_user = ReceptionRegister.objects.get(
                    mobile_number=mobile_number)
                refresh['doctor_id'] = reception_user.doctor_id
            except ReceptionRegister.DoesNotExist:
                error_doctor.error(
                    f"Reception user not found for mobile number: {mobile_number}")
            except Exception as e:
                error_doctor.error(f"Error retrieving reception user for mobile number {mobile_number}: {str(e)}")
   
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    # def generate_tokens(self, mobile_number, user_id, user_type):
    #     # Create a refresh token
    #     refresh = RefreshToken()
    #     # Set custom claims
    #     refresh['doctor_id'] = user_id
    #     refresh['user_type'] = user_type
    #     refresh['mobile_number'] = mobile_number
   
    #     try:
    #         if user_type == 'doctor':
    #             user = DoctorRegister.objects.get(id=user_id)
    #             refresh['is_verified'] = user.is_verified
    #             refresh['is_active'] = user.is_active
    #         elif user_type == 'clinic':
    #             user = ClinicRegister.objects.get(id=user_id)
    #             refresh['clinic_id'] = user.doctor_id
    #         elif user_type == 'reception':
    #             user = ReceptionRegister.objects.get(id=user_id)
    #             refresh['reception_id'] = user.doctor_id
    #     except (DoctorRegister.DoesNotExist, ClinicRegister.DoesNotExist, ReceptionRegister.DoesNotExist) as e:
    #         error_doctor.error(f"User not found for mobile number: {
    #                            mobile_number} - {str(e)}")
   
    #     return {
    #         'refresh': str(refresh),
    #         'access': str(refresh.access_token),
    #     }

class DoctorDetailApi(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get('mobile_number')  
        if not mobile_number:
            return Response({"error": "Mobile number is required.",},status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor_register = DoctorRegister.objects.filter(mobile_number=mobile_number).first()
            if not doctor_register:
                return Response({"error": "This mobile number is not registered.","mobile_number": mobile_number},status=status.HTTP_404_NOT_FOUND)
            doctor_details = PersonalsDetails.objects.filter(doctor=doctor_register)
            if not doctor_details.exists():
                return Response({"success": "Kindly update your details.","mobile_number": mobile_number},status=status.HTTP_200_OK)
            serializer = DoctorDetailSerializer(doctor_details, many=True)
            doctor_details_with_mobile = [
                {**detail, "mobile_number": mobile_number} for detail in serializer.data
            ]
            return Response(doctor_details_with_mobile)
        except Exception as e:
            error_doctor.error(f"Error occurred while processing GET request: {e}")
            return Response({"error": "An error occurred while processing the request.","mobile_number": mobile_number},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        try:
            if not mobile_number:
                error_doctor.error('Mobile number is missing in the request')
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            
            doctor_register = DoctorRegister.objects.filter(mobile_number=mobile_number).first()
            if not doctor_register:
                error_doctor.error('Mobile number %s is not Registered', mobile_number)
                return Response({"error": "Mobile number is not Registered"}, status=status.HTTP_404_NOT_FOUND)
            
            existing_doctor_detail = PersonalsDetails.objects.filter(doctor=doctor_register).first()
            if existing_doctor_detail:
                error_doctor.error('User details already exist for %s mobile number', mobile_number)
                return Response({"error": "User details already exist for this mobile number"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Make a copy of request.data to modify it
            request_data = request.data.copy()
            request_data["doctor"] = doctor_register.pk

            serializer = DoctorDetailSerializer(data=request_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                info_doctor.info('Doctor details saved successfully')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                error_doctor.error(f'Invalid data: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            error_doctor.error(f'Exception occurred: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def post(self, request, *args, **kwargs):
    #     mobile_number = request.data.get("mobile_number")
        
    #     if not mobile_number:
    #         return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST) 
        
    #     try:
    #         # Check for existing doctor detail
    #         if PersonalsDetails.objects.filter(doctor__mobile_number=mobile_number).exists():
    #             return Response({"error": "Doctor detail already exists for this mobile number"}, status=status.HTTP_400_BAD_REQUEST)
            
    #         # # Get the doctor register
    #         # doctor_register = DoctorRegister.objects.get(mobile_number=mobile_number)
            
    #         # # Prepare mutable data for the serializer
    #         # mutable_data = request.data.copy()
    #         # mutable_data["doctor"] = doctor_register.pk
            
    #         # Validate and save doctor details
    #         doctor_serializer = DoctorDetailSerializer(data=request.data)
    #         if doctor_serializer.is_valid():
    #             doctor_serializer.save()
    #             return Response(doctor_serializer.data, status=status.HTTP_201_CREATED)
            
    #         return Response(doctor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #     except DoctorRegister.DoesNotExist:
    #         return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         # logger.error(f"Exception occurred: {e}")
    #         return Response({"error": "An unexpected error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



     
    def put(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        try:
            if not mobile_number:
                error_doctor.error('Mobile number is missing in the request')
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            
            doctor_register = DoctorRegister.objects.filter(mobile_number=mobile_number).first()
            if not doctor_register:
                error_doctor.error('Mobile number %s is not Registered', mobile_number)
                return Response({"error": "Mobile number is not Registered"}, status=status.HTTP_404_NOT_FOUND)
            
            existing_doctor_detail = PersonalsDetails.objects.filter(doctor=doctor_register).first()
            if not existing_doctor_detail:
                error_doctor.error('No existing details found for mobile number %s', mobile_number)
                return Response({"error": "No existing details found for this mobile number"}, status=status.HTTP_404_NOT_FOUND)
            
            # Make a copy of request.data to modify it
            request_data = request.data.copy()
            request_data["doctor"] = doctor_register.pk
            
            serializer = DoctorDetailSerializer(existing_doctor_detail, data=request_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                info_doctor.info('Doctor details updated successfully')
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                error_doctor.error(f'Invalid data: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            error_doctor.error(f'Exception occurred: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, format=None):
        mobile_number = request.data.get('mobile_number')
        try:
            if not mobile_number:
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user_details = PersonalsDetails.objects.get(doctor__mobile_number=mobile_number)
            except Exception as e:
                return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)        
            serializer = DoctorDetailSerializer(user_details, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'User Details Updated'},status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SelectQualification(APIView):
    def get(self, request, format=None):
        try:
            doctor_id = request.query_params.get('doctor_id')
            if not doctor_id:
                return Response({'error': 'doctor_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
            doctor = DoctorRegister.objects.get(id=doctor_id)
            qualifications = Qualification.objects.filter(doctor=doctor)
            serializer = QualificationSerializer(qualifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DoctorRegister.DoesNotExist:
            return Response({'error': f'Doctor with id {doctor_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, format=None):
        try:
            doctor_id = request.data.get('doctor_id') 
            doctor = DoctorRegister.objects.get(id=doctor_id)
            qualifications_data = request.data.get('qualifications', [])
            for qualification_data in qualifications_data:
                qualification_id = qualification_data.get('id')
                is_selected = qualification_data.get('is_selected', False)
                try:
                    qualification = Qualification.objects.get(id=qualification_id, doctor=doctor)
                    qualification.is_selected = is_selected
                    qualification.save()
                except Qualification.DoesNotExist:
                    return Response({'error': f'Qualification with id {qualification_id} does not exist for doctor {doctor_id}'}, status=status.HTTP_404_NOT_FOUND)
            updated_qualifications = Qualification.objects.filter(doctor=doctor)
            serializer = QualificationSerializer(updated_qualifications, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DoctorRegister.DoesNotExist:
            return Response({'error': f'Doctor with id {doctor_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DoctordetailsUsingID(APIView):
    def get(self, request, format=None):
        try:
            doctor_id = request.query_params.get("id")
            if not doctor_id:
                return Response({"error": "id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
            user_details = PersonalsDetails.objects.filter(doctor_id=doctor_id).first()
            if not user_details:
                return Response({'error': 'Doctor details not found for the provided id'}, status=status.HTTP_404_NOT_FOUND)
        
            serializer = DetailSerializer(user_details)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class SearchDoctor(APIView):
    def get(self, request):
        query = request.query_params.get("query", None)
        if query:
            filter_by_name = Q(name__icontains=query)
            filter_by_specializations = Q(specialization__icontains=query)

            # Pehle is_verified filter lagana
            doctors = PersonalsDetails.objects.filter(
                (filter_by_name | filter_by_specializations) & Q(is_verified=True)
            )

            if not doctors.exists():
                return Response({"error": "No doctors found matching the query."}, status=status.HTTP_404_NOT_FOUND)

            serializer = SearchDetailsSerializer(doctors, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Please enter a query to search for doctors."}, status=status.HTTP_400_BAD_REQUEST)

class DoctorFeedbackApi(APIView):
    def post(self, request, format=None):
        serializer = DoctorFeedbackSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
           
            return Response({"success": "Feedback submitted successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": "data is not valid", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DoctorName(APIView):
    def get(self, request):
        doctor_id = request.query_params.get('doctor_id')
        if doctor_id:
            doctors = PersonalsDetails.objects.filter(doctor_id=doctor_id)
        else:
            return Response({'error': 'doctor id is required'})
        serializer = DoctornameSerializer(doctors, many=True)
        return Response(serializer.data)
    

    
class GetHospitalName(APIView):
    def get(self,request):
        try:
            doctor_id=request.query_params.get('doctor_id')
            if not doctor_id:
                return Response({"error":"Doctor ID is required."}, status=status.HTTP_400_BAD_REQUEST)
            doctor_details=PersonalsDetails.objects.get(doctor_id=doctor_id)
            if not doctor_details:
                return Response({"error":"Doctor Details not found for the given ID"}, status= status.HTTP_404_NOT_FOUND)
            hospital_name = doctor_details.hospital_name
            return Response({"hospital_name":hospital_name}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CountDoctors(APIView):
    def get(self, request):
        try:
            total_doctors = PersonalsDetails.objects.count()
            verified_doctors = PersonalsDetails.objects.filter(is_verified=True).count()
            not_verified_doctors = PersonalsDetails.objects.filter(is_verified=False).count()
            active_doctors = PersonalsDetails.objects.filter(is_active=True).count()
            inactive_doctors = PersonalsDetails.objects.filter(is_active=False).count()
 
            data=[{
                "total_doctors": total_doctors},{
                "verified_doctors":verified_doctors},{
                "not_verified_doctors":not_verified_doctors},{
                "active_doctors":active_doctors},{
                "inactive_doctors":inactive_doctors
                }]  
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class DoctorBook(APIView):
    def post(self, request, format=None):
        patient_id = request.data.get("patient")
        doctor_id = request.data.get("doctor")
        appointment_slot_id = request.data.get("appointment_slot")
 
        if not patient_id or not doctor_id or not appointment_slot_id:
            return Response({"error": "Patient ID, doctor ID, and appointment slot ID are required."}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            patient = PatientVarryDetails.objects.get(id=patient_id)
        except PatientVarryDetails.DoesNotExist:
            return Response({"error": "Invalid patient ID."}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            doctor = PersonalsDetails.objects.get(doctor_id=doctor_id)
        except DoctorDetail.DoesNotExist:
            return Response({"error": "Invalid doctor ID."}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            appointment_slot = Appointmentslots.objects.get(
                pk=appointment_slot_id, doctor__doctor_id=doctor_id)
        except Appointmentslots.DoesNotExist:
            return Response({"error": "No appointment slot found for the given doctor and slot ID."}, status=status.HTTP_404_NOT_FOUND)
 
        if appointment_slot.is_booked:
            return Response({"error": "Appointment slot is already booked."}, status=status.HTTP_400_BAD_REQUEST)
 
 
        previous_appointments = Appointmentslots.objects.filter(
            booked_by__mobile_number=patient.mobile_number
          
        )
 
        if previous_appointments.exists():
            appointment_slot.appointment_type = "follow-up"
        else:
            appointment_slot.appointment_type = "walk-in"
 
        appointment_slot.is_booked = True
        appointment_slot.booked_by = patient
        appointment_slot.is_patient = False
        appointment_slot.save()
 
        serializer = DoctorSlotSerializer(appointment_slot)
        return Response({"success": "Slot confirmed successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)

class SymptomsSearch(APIView):
    def get(self, request, *args, **kwargs):
        name_query = request.query_params.get('name', None)
        if name_query:
            symptoms = Symptoms.objects.filter(
                symptoms_name__icontains=name_query)
            if not symptoms.exists():
                new_symptom = Symptoms.objects.create(symptoms_name=name_query)
                symptoms = Symptoms.objects.filter(id=new_symptom.id)
        else:
 
            symptoms = Symptoms.objects.all()
        serializer = SymptomsSerializer(symptoms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
class SymptomsDetailView(APIView):
    
    def get(self, request, *args, **kwargs):
        appointment_id = request.query_params.get("appointment_id")

        if not appointment_id:
            return Response({"error": "appointment_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        symptom_details = SymptomsDetail.objects.select_related(
            'appointment', 'symptoms').filter(appointment_id=appointment_id)

        if not symptom_details.exists():
            return Response({"error": "No SymptomsDetail found ."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SymptomsDetailSerializer(symptom_details, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        symptoms_id = request.data.get("symptoms")
        appointment_id = request.data.get("appointment")

        if not symptoms_id or not appointment_id:
            return Response({"error": "symptoms and appointment are required."}, status=status.HTTP_400_BAD_REQUEST)

        symptom_detail = SymptomsDetail.objects.filter(
            symptoms_id=symptoms_id, appointment_id=appointment_id).first()
        serializer = SymptomsDetailSerializer(
            symptom_detail, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "symptoms details saved successfully"}, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        symptoms_id = request.data.get("symptoms_id")
        appointment_id = request.data.get("appointment_id")
        symptoms_name = request.data.get("symptoms_name")

        if not symptoms_id:
            return Response({"error": "symptoms_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not appointment_id:
            return Response({"error": "appointment_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            symptom_detail = SymptomsDetail.objects.get(
                id=symptoms_id, appointment_id=appointment_id)

            if symptoms_name:
                symptom = symptom_detail.symptoms
                symptom.symptoms_name = symptoms_name
                symptom.save()

            serializer = SymptomsDetailSerializer(
                symptom_detail, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data
                response_data['symptoms_name'] = symptom.symptoms_name
                return Response({"success": "symptoms details update successfully"}, status = status.HTTP_201_CREATED )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except SymptomsDetail.DoesNotExist:
            return Response({"error": "SymptomsDetail not found."}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, *args, **kwargs):
        symptoms_id = request.data.get("symptoms_id")
        appointment_id = request.data.get("appointment_id")

        if not appointment_id:
            return Response({"error": "appointment_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            symptoms_details = SymptomsDetail.objects.filter(symptoms_id=symptoms_id,
                appointment_id=appointment_id)
            if not symptoms_details.exists():
                return Response({"error": "SymptomsDetail not found."}, status=status.HTTP_404_NOT_FOUND)


            symptoms_details.delete()
            return Response({"success": "SymptomsDetail deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
        
class PersonalDoctorDetail(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get('mobile_number')
        if not mobile_number:
            return Response({"error": "Mobile number is required.", }, status=status.HTTP_400_BAD_REQUEST)
        try:
            
            doctor_register = DoctorRegister.objects.filter(
                mobile_number=mobile_number).first()
            if not doctor_register:
                return Response({"error": "This mobile number is not registered.", "mobile_number": mobile_number}, status=status.HTTP_404_NOT_FOUND)
            doctor_details = PersonalsDetails.objects.filter(
                doctor=doctor_register)
            if not doctor_details.exists():
                return Response({"success": "Kindly update your details.", "mobile_number": mobile_number}, status=status.HTTP_200_OK)
            serializer = PersonalsDetailsSerializer(doctor_details, many=True)
            doctor_details_with_mobile = [
                {**detail, "mobile_number": mobile_number} for detail in serializer.data
            ]
            return Response(doctor_details_with_mobile)
        except Exception as e:
            error_doctor.error(
                f"Error occurred while processing GET request: {e}")
            return Response({"error": "An error occurred while processing the request.", "mobile_number": mobile_number}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def post(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        try:
            if not mobile_number:
                error_doctor.error('Mobile number is missing in the request')
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
 
            doctor_register = DoctorRegister.objects.filter(
                mobile_number=mobile_number).first()
            if not doctor_register:
                error_doctor.error(
                    'Mobile number %s is not Registered', mobile_number)
                return Response({"error": "Mobile number is not Registered"}, status=status.HTTP_404_NOT_FOUND)
 
            existing_doctor_detail = PersonalsDetails.objects.filter(
                doctor=doctor_register).first()
            if existing_doctor_detail:
                error_doctor.error(
                    'User details already exist for %s mobile number', mobile_number)
                return Response({"error": "User details already exist for this mobile number"}, status=status.HTTP_400_BAD_REQUEST)
 
            request_data = request.data.copy()
            request_data["doctor"] = doctor_register.pk
 
            serializer = PersonalsDetailsSerializer(
                data=request_data, partial=True)
            if serializer.is_valid():
                serializer.save(is_update=True)
                info_doctor.info('Doctor details saved successfully')
                return Response({"success": "Doctor details saved successfully"}, status = status.HTTP_201_CREATED)
            else:
                error_doctor.error(f'Invalid data: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
        except Exception as e:
            error_doctor.error(f'Exception occurred: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def put(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        try:
            if not mobile_number:
                error_doctor.error('Mobile number is missing in the request')
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
 
            doctor_register = DoctorRegister.objects.filter(
                mobile_number=mobile_number).first()
            if not doctor_register:
                error_doctor.error(
                    'Mobile number %s is not Registered', mobile_number)
                return Response({"error": "Mobile number is not Registered"}, status=status.HTTP_404_NOT_FOUND)
 
            existing_doctor_detail = PersonalsDetails.objects.filter(
                doctor=doctor_register).first()
            if not existing_doctor_detail:
                error_doctor.error(
                    'No existing details found for mobile number %s', mobile_number)
                return Response({"error": "No existing details found for this mobile number"}, status=status.HTTP_404_NOT_FOUND)
 
            request_data = request.data.copy()
            request_data["doctor"] = doctor_register.pk
 
            serializer = PersonalsDetailsSerializer(
                existing_doctor_detail, data=request_data, partial=True)
            if serializer.is_valid():
                serializer.save(is_update=True)
                info_doctor.info('Doctor details updated successfully')
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                error_doctor.error(f'Invalid data: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
        except Exception as e:
            error_doctor.error(f'Exception occurred: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
class DoctorAddress(APIView):
    def post(self, request, format=None):
        doctor_id = request.data.get('doctor_id')
        try:
            doctor = DoctorRegister.objects.get(id=doctor_id)
        except DoctorRegister.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
 
        data = request.data.copy()
        data['doctor'] = doctor.id
 
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save(is_update=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def get(self, request, format=None):
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            doctor = DoctorRegister.objects.get(id=doctor_id)
        except DoctorRegister.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
 
        addresses = Address.objects.filter(doctor=doctor)
        if not addresses.exists():
            return Response({"success": "Kindly update your details."}, status=status.HTTP_200_OK)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def put(self, request, format=None):
        doctor_id = request.data.get('doctor_id')
        address_id = request.data.get('address_id')
 
        if not address_id:
            return Response({"error": "address_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            doctor = DoctorRegister.objects.get(id=doctor_id)
        except DoctorRegister.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
 
        try:
            address = Address.objects.get(id=address_id, doctor=doctor)
        except Address.DoesNotExist:
            return Response({"error": "Address not found for the given doctor."}, status=status.HTTP_404_NOT_FOUND)
 
        data = request.data.copy()
        data['doctor'] = doctor.id
 
        serializer = AddressSerializer(address, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(is_update=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class OpdDays(APIView):
    def get(self, request, format=None):
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = DoctorRegister.objects.get(id=doctor_id)
        except DoctorRegister.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        opddays = Opd.objects.filter(doctor=doctor)
        if not opddays.exists():
            return Response({"success": "Kindly update your details."}, status=status.HTTP_200_OK)
        serializer = OpdDaysSerializers(opddays, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        doctor_id = request.data.get("doctor_id")

        if not doctor_id:
            return Response({"error": "The 'doctor_id' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = DoctorRegister.objects.get(id=doctor_id)
        except DoctorRegister.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
        existing_doctor_detail = Opd.objects.filter(
            doctor=doctor).first()
        if existing_doctor_detail:
            return Response({"error": "Opd deatils already exist "}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['doctor'] = doctor.id

        serializer = OpdDaysSerializers(data=data)

        if serializer.is_valid():
            serializer.save(is_update=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

    def put(self, request, format=None):
        doctor_id = request.data.get("doctor_id")

        if not doctor_id:
            return Response({"error": "The 'doctor_id' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = DoctorRegister.objects.get(id=doctor_id)
        except DoctorRegister.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        opdday = Opd.objects.filter(doctor=doctor)

        if not opdday.exists():
            return Response({"error": "OPD Day entry not found for the provided doctor."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['doctor'] = doctor.id

        updated_entries = []
        for opd_instance in opdday:
            serializer = OpdDaysSerializers(opd_instance, data=data, partial=True)
            if serializer.is_valid():
                serializer.save(is_update=True)
                updated_entries.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(updated_entries, status=status.HTTP_200_OK)

    def delete(self, request):
        doctor = request.query_params.get("doctor_id")

        if not doctor:
            return Response({"error": " 'doctor_id' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            opd = Opd.objects.get( doctor_id=doctor)
            opd.delete()
            return Response({"success": "OPD record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except OpdDays.DoesNotExist:
            return Response({"error": "OPD record not found for the given doctor ID and OPD ID"}, status=status.HTTP_404_NOT_FOUND)
 
 
class OpdTimeView(APIView):
     
    def get(self, request, format=None):
        opd_id = request.query_params.get('opd_id')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
 
        if opd_id:
            opd_times = OpdTime.objects.filter(time__id=opd_id)
            if start_time:
                opd_times = opd_times.filter(start_time=start_time)
            if end_time:
                opd_times = opd_times.filter(end_time=end_time)
 
            if not opd_times.exists():
                return Response({"error": "No time entries found for this OPD."}, status=status.HTTP_404_NOT_FOUND)
            serializer = OpdTimeSerializer(opd_times, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
 
   
        opd_times = OpdTime.objects.all()
        if start_time:
            opd_times = opd_times.filter(start_time=start_time)
        if end_time:
            opd_times = opd_times.filter(end_time=end_time)
 
        serializer = OpdTimeSerializer(opd_times, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request):
        opd_id = request.data.get('opd_id')
        if not opd_id:
            return Response({"error": "OPD ID is required."}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            opd = Opd.objects.get(id=opd_id)
        except Opd.DoesNotExist:
            return Response({"error": "OPD not found."}, status=status.HTTP_404_NOT_FOUND)
 
        data = request.data.copy()
        data['time'] = opd.id  
 
        serializer = OpdTimeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def put(self, request, time_id=None):
        opd_id = request.data.get('opd_id')
        time_id = request.data.get('time_id')
        if not opd_id or not time_id:
            return Response({"error": "Both OPD ID and time ID are required."}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            opd = Opd.objects.get(id=opd_id)
            opd_time = OpdTime.objects.get(id=time_id, time=opd)  
        except (Opd.DoesNotExist, OpdTime.DoesNotExist):
            return Response({"error": "OPD or OpdTime not found."}, status=status.HTTP_404_NOT_FOUND)
 
        serializer = OpdTimeSerializer(opd_time, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
 
    def delete(self, request):
        time_id = request.query_params.get("time_id")
 
        if not time_id:
            return Response({"error": " 'time_id' is required."}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            opd = OpdTime.objects.filter( id=time_id)
            opd.delete()
            return Response({"success": "Time record deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except OpdTime.DoesNotExist:
            return Response({"error": "Time record not found"}, status=status.HTTP_404_NOT_FOUND)
       
 
class DoctorDetailSummary(APIView):
    def get(self, request, format=None):
        doctor_id = request.query_params.get('doctor_id')
 
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            doctor = DoctorRegister.objects.get(id=doctor_id)
        except DoctorRegister.DoesNotExist:
            return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
 
        doctor_summary = {
            "doctor_id": doctor.id,
            "personal_details": False,
            "address": False,
            "opd_days": False,
        }
 
        if PersonalsDetails.objects.filter(doctor=doctor).exists():
            doctor_summary["personal_details"] = True
        if Address.objects.filter(doctor=doctor).exists():
            doctor_summary["address"] = True
        if Opd.objects.filter(doctor=doctor).exists():
            doctor_summary["opd_days"] = True
 
        return Response(doctor_summary, status=status.HTTP_200_OK)
    



class ViewDoctorDocument(APIView):
    def get(self, request, format=None):
        try:
            # Get doctor_id from query parameters
            doctor_id = request.query_params.get('doctor_id')
 
            if not doctor_id:
                return Response({"error": "Doctor ID is required"}, status=status.HTTP_400_BAD_REQUEST)
 
            # Fetch the doctor details based on the provided doctor_id
            doctor = DoctorRegister.objects.filter(id=doctor_id).first()
            if not doctor:
                return Response({"error": "Doctor with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
 
            # Fetch the PersonalDetails object associated with the doctor
            personal_details = PersonalsDetails.objects.filter(doctor=doctor).first()
            if not personal_details or not personal_details.doc_file:
                return Response({"error": "Document not found for this doctor"}, status=status.HTTP_404_NOT_FOUND)
 
            # Determine MIME type for the document
            file_path = personal_details.doc_file.path
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'  # Fallback MIME type
 
            # Check if the file exists and return it in the response
            try:
                response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
                response['Content-Disposition'] = f'attachment; filename="{personal_details.doc_file.name}"'
                return response
            except FileNotFoundError:
                raise Http404("File not found")
       
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Accessibility(APIView):
    def get(self, request, format=None):
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response({"error": "Doctor ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        doctor = DoctorRegister.objects.filter(id=doctor_id).first()
        if not doctor:
            return Response({"error": "Doctor with this ID does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if doctor.is_active==False:
            return Response({"error": " you are currently inactive !your profile in underprocessing."}, status=status.HTTP_400_BAD_REQUEST)
            
        if doctor.is_verified==False:
            personals_details = PersonalsDetails.objects.filter(doctor=doctor).first()
            address = Address.objects.filter(doctor=doctor).first()
            opd = Opd.objects.filter(doctor=doctor).first()
            opd_time = OpdTime.objects.filter(time__doctor=doctor).first()

            if all([personals_details, address, opd, opd_time]):
                return Response({"success": " Your are unverified ! kindly fill your details.","is_verified": doctor.is_verified, "is_active": doctor.is_active}, status=status.HTTP_200_OK)
        
            else:
                return Response({"error": "Please fill all your details then we will allow.","is_verified": doctor.is_verified, "is_active": doctor.is_active}, status=status.HTTP_400_BAD_REQUEST)
        
        
        status_response = {"is_verified": doctor.is_verified, "is_active": doctor.is_active}
        return Response(status_response, status=status.HTTP_200_OK)
 
 

class DoctorListBySpecialization(APIView):
    def get(self, request):
        specialization = request.query_params.get('specialization', None)
        
        if specialization:
            # Filtering for verified doctors only
            doctors = PersonalsDetails.objects.filter(
                specialization__icontains=specialization,
                is_verified=True
            )
        else:
            # All verified doctors if no specialization is provided
            doctors = PersonalsDetails.objects.filter(is_verified=True)

        serializer = SearchDetailsSerializer(doctors, many=True)
        
        if not serializer.data:
            return Response({"error": "No doctors found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)