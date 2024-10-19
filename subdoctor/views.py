
import logging
from doctor.models import DoctorRegister
from subdoctor.models import SubdoctorDetail, SubdoctorRegister
from subdoctor.serializers import SubdoctorDetialsSerializers, SubdoctorRegisterSerializer
import random
import re
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q

from subdoctor.utils import login_otp, register_otp, register_sms
error_subdoctor = logging.getLogger('error_subdoctor')
info_subdoctor = logging.getLogger('info_subdoctor')
warning_subdoctor= logging.getLogger('warning_subdoctor')

# Create your views here.
class SubdoctorRegisterApi(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
        try:
            if not mobile_number:
                error_subdoctor.error("Mobile number is required")
                return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not re.match(r"^\d{10}$", mobile_number):
                error_subdoctor.error("Please enter a 10-digit number.")
                return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
            if SubdoctorRegister.objects.filter(mobile_number=mobile_number).exists():
                error_subdoctor.error("Mobile number is already registered: %s", mobile_number)
                return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                info_subdoctor.info("Mobile number: %s", mobile_number)
                cache.set("Doctor" + str(mobile_number), mobile_number, timeout=300)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            otp = ''.join(random.choices('0123456789', k=6))
            # otp=register_otp(mobile_number)
            print(otp)
            info_subdoctor.info("OTP generated for mobile number %s: %s", mobile_number, otp)
            cache.set(mobile_number, otp, timeout=300)
            return Response({"success": "OTP generated successfully", "otp": otp}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    
    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            otp = request.data.get("otp")
            info_subdoctor.info("Mobile number: %s, OTP: %s", mobile_number, otp)
            if not mobile_number or not otp:
                error_subdoctor.error("Mobile number and OTP are required")
                return Response({"error": "Mobile number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
            cached_mobile_number = cache.get("Doctor" + str(mobile_number))
            if not re.match(r"^\d{10}$", mobile_number):
                error_subdoctor.error("Please enter a 10-digit number.")
                return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
            if SubdoctorRegister.objects.filter(mobile_number=mobile_number).exists():
                error_subdoctor.error("Mobile number is already registered: %s", mobile_number)
                return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)
            if cached_mobile_number != mobile_number:
                error_subdoctor.error("Mobile number %s is not registered or OTP session expired. Resend OTP.", mobile_number)
                return Response({"error": "Mobile number is not registered. Resend OTP."}, status=status.HTTP_400_BAD_REQUEST)
            cached_otp = cache.get(mobile_number)
            if cached_otp is None:
                error_subdoctor.error("Session expired. Please request a new OTP. %s", mobile_number)
                return Response({"error": "Session expired. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
            if otp != cached_otp:
                error_subdoctor.error("Incorrect OTP for mobile number %s", mobile_number)
                return Response({"error": "Incorrect OTP. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
            doctor_serializer = SubdoctorRegisterSerializer(data=request.data)
            if doctor_serializer.is_valid():
                doctor_serializer.save()
                info_subdoctor.info("User with mobile number %s successfully registered", mobile_number)
                # register_sms(mobile_number)
                return Response({'success': "You are successfully registered!"}, status=status.HTTP_201_CREATED)
            else:
                return Response(doctor_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SubdocterLoginApi(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
        try:
            if not mobile_number:
                error_subdoctor.error("Mobile number is required")
                return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not re.match(r"^\d{10}$", mobile_number):
                error_subdoctor.error("Please enter a 10-digit number.")
                return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
            if not SubdoctorRegister.objects.filter(mobile_number=mobile_number).exists():
                error_subdoctor.error("Mobile number %s is not registered. Please register first.", mobile_number)
                return Response({"error": "Mobile number is not registered. Please register first."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                otp = ''.join(random.choices('0123456789', k=6))
                otp = login_otp(mobile_number)
                cache.set(mobile_number, otp, timeout=60)
                print(otp)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            info_subdoctor.info("OTP generated successfully %s", otp)
            return Response({"success": "OTP generated successfully", "otp": otp},status=status.HTTP_200_OK)
        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            error_subdoctor.error(error_message)
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            otp_entered = request.data.get("otp")

            if not mobile_number or not otp_entered:
                error_subdoctor.error("Mobile number and OTP are required")
                return Response({"error": "Mobile number and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)

            cached_otp = cache.get(mobile_number)
            if not cached_otp:
                error_subdoctor.error("OTP has expired or mobile number is not registered: %s", mobile_number)
                return Response({"error": "OTP has expired or mobile number is not registered"}, status=status.HTTP_400_BAD_REQUEST)

            if otp_entered != cached_otp:
                error_subdoctor.error("Incorrect OTP entered for mobile number: %s", mobile_number)
                return Response({"error": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)
            user = SubdoctorRegister.objects.get(mobile_number=mobile_number)
            user_id = user.pk  
            tokens = self.generate_tokens(mobile_number, user_id)
            info_subdoctor.info("Login successful for mobile number: %s", mobile_number)
            return Response({
                'success': "Login successful!",
                'user_id': user_id,
                'mobile_number': mobile_number,
                'is_doctor':False,
                **tokens
            }, status=status.HTTP_201_CREATED)

        except SubdoctorRegister.DoesNotExist:
            error_subdoctor.error("User not found for mobile number: %s", mobile_number)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            error_message = f"Internal Server Error: {str(e)}"
            error_subdoctor.error(error_message)
            return Response({"error": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def generate_tokens(self, mobile_number, user_id):
        refresh = RefreshToken()
        refresh['user_id'] = user_id  
        refresh['mobile_number'] = mobile_number  
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

class SubSubdoctorDetailApi(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get('mobile_number')  
        if not mobile_number:
            return Response({"error": "Mobile number is required.",},status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor_register = SubdoctorRegister.objects.filter(mobile_number=mobile_number).first()
            if not doctor_register:
                return Response({"error": "This mobile number is not registered.","mobile_number": mobile_number},status=status.HTTP_404_NOT_FOUND)
            doctor_details = SubPersonalsDetails.objects.filter(subdoctor=doctor_register)
            if not doctor_details.exists():
                return Response({"message": "Kindly update your details.","mobile_number": mobile_number},status=status.HTTP_200_OK)
            serializer = SubdoctorDetialsSerializers(doctor_details, many=True)
            doctor_details_with_mobile = [
                {**detail, "mobile_number": mobile_number} for detail in serializer.data
            ]
            return Response(doctor_details_with_mobile)
        except Exception as e:
            error_subdoctor.error(f"Error occurred while processing GET request: {e}")
            return Response({"error": "An error occurred while processing the request.","mobile_number": mobile_number},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        try:
            if not mobile_number:
                error_subdoctor.error('Mobile number is missing in the request')
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            
            # existing_doctor_detail = ClinicDetail.objects.filter(clinic__mobile_number=mobile_number).first()
            # if existing_doctor_detail:
            #     error_subdoctor.error('User details already exist for %s mobile number', mobile_number)
            #     return Response({"error": "User details already exist for this mobile number"}, status=status.HTTP_400_BAD_REQUEST)
            
            doctor_register = SubdoctorRegister.objects.filter(mobile_number=mobile_number).first()
            if not doctor_register:
                error_subdoctor.error('Mobile number %s is not Registered', mobile_number)
                return Response({"error": "Mobile number is not Registered"}, status=status.HTTP_404_NOT_FOUND)
            
            # Create a mutable copy of the request data
            data = request.data.copy()
            data["subdoctor"] = doctor_register.pk
            print(data)
            # import pdb;pdb.set_trace()
            serializer = SubdoctorDetialsSerializers(data=data)
            if serializer.is_valid():
                serializer.save()
                info_subdoctor.info('Doctor details saved successfully')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                error_subdoctor.error(f'Invalid data: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, format=None):
        mobile_number = request.data.get('mobile_number')
        try:
            if not mobile_number:
                error_subdoctor.error('Mobile number is missing in the request')
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user_details = SubPersonalsDetails.objects.get(doctor__mobile_number=mobile_number)
            except SubdoctorDetail.DoesNotExist:
                error_subdoctor.error('User details not found for the provided mobile number')
                return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)
            serializer = SubdoctorDetialsSerializers(user_details, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                info_subdoctor.info('User Details Updated successfully')
                return Response({'success': 'User Details Updated'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, format=None):
        mobile_number = request.data.get('mobile_number')
        try:
            if not mobile_number:
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user_details = SubPersonalsDetails.objects.get(doctor__mobile_number=mobile_number)
            except Exception as e:
                return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)        
            serializer = SubdoctorDetialsSerializers(user_details, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'User Details Updated'},status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AllSubdoctorDetail(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get('mobile_number')

        if not mobile_number:
            return Response({"error": "Mobile number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the doctor register using the mobile number
            doctor_register = SubdoctorRegister.objects.get(mobile_number=mobile_number)

            # Fetch all subdoctor details associated with the doctor register
            subdoctor_details = SubPersonalsDetails.objects.filter(doctor=doctor_register)

            # Serialize the subdoctor details
            serializer = SubdoctorDetialsSerializers(subdoctor_details, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except DoctorRegister.DoesNotExist:
            return Response({"error": f"No doctor found with mobile number {mobile_number}"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)