import hashlib
import mimetypes
import random
from django.http import FileResponse, Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from .serializers import DocDetailSerializer, DocDetailforSerializer, DoctorDetailAdmin, DoctorRegisterSerializer
from doctor.models import DoctorDetail, DoctorRegister, PersonalsDetails
from .models import DigiAdminLogin, hash_value
 
 
class DigiAdminLoginAPIView(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        password = request.query_params.get('password')
 
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
 
        hashed_username = hash_value(username)
        hashed_password = hash_value(password)
 
        try:
            login_instance = DigiAdminLogin.objects.get(
                username=hashed_username)
   
            if check_password(password, login_instance.password) | (login_instance.password == hashed_password):
                otp = self.generate_otp()
                cache_key = f'otp_{hashed_username}'
                cache.set(cache_key, otp, timeout=60)
 
                if self.send_otp_email(username, otp):
                    return Response({'success': 'An OTP has been sent to your registered email'}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Failed to send email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
        except DigiAdminLogin.DoesNotExist:
            return Response({"error": "The username and password combination is incorrect"}, status=status.HTTP_404_NOT_FOUND)
 
    def post(self, request):
        username = request.data.get('username')
        otp = request.data.get('otp')
        password = request.data.get('password')
 
        if not username or not otp or not password:
            return Response({"error": "Username, OTP, and password are required"}, status=status.HTTP_400_BAD_REQUEST)
 
        hashed_username = hash_value(username)
        hashed_password = hash_value(password)
        cache_key = f'otp_{hashed_username}'
 
        cached_otp = cache.get(cache_key)
 
        if cached_otp is None:
            return Response({"error": "OTP has expired or is invalid"}, status=status.HTTP_400_BAD_REQUEST)
 
        if str(cached_otp) == str(otp):
            try:
                login_instance = DigiAdminLogin.objects.get(
                    username=hashed_username)
                if check_password(password, login_instance.password) | (login_instance.password == hashed_password):
                    return Response({'success': 'Login successful'}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
            except DigiAdminLogin.DoesNotExist:
                return Response({"error": "Username not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
 
    def generate_otp(self):
        """Generate a 6-digit OTP"""
        return random.randint(100000, 999999)
 
    def send_otp_email(self, username, otp):
        subject = 'Your OTP for Login'
        message = f'Your OTP for login is {otp}. It is valid for 1 minute. Thank you.'
 
        try:
            send_mail(
                subject,
                message,
                'username',  
                [username]
            )
            return True
        except Exception as e:
       
            return False
       
class RequestPassword(APIView):
    def get(self, request):
        username = request.query_params.get('username')
        if not username:
            return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)
 
        hashed_username = self.hash_value(username)
        try:
            login_instance = DigiAdminLogin.objects.get(
                username=hashed_username)
        except DigiAdminLogin.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
 
        otp = self.generate_otp()
        cache_key = f'otp_{hashed_username}'
        cache.set(cache_key, otp, timeout=300)  
 
        if self.send_otp_email(username, otp):
            return Response({'success': 'An OTP has been sent to your registered email.'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def post(self, request):
        username = request.data.get('username')
        otp = request.data.get('otp')
 
        if not username or not otp:
            return Response({"error": "Username and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)
 
        hashed_username = self.hash_value(username)
        cache_key = f'otp_{hashed_username}'
        cached_otp = cache.get(cache_key)
 
        if cached_otp is None:
            return Response({"error": "OTP has expired or is invalid."}, status=status.HTTP_400_BAD_REQUEST)
 
        if str(cached_otp) == str(otp):
            cache.delete(cache_key)
            return Response({'success': 'OTP verified successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
 
    def generate_otp(self):
        """Generate a secure 6-digit OTP."""
        return random.randint(100000, 999999)
 
    def send_otp_email(self, username, otp):
        """Send OTP to the user's email."""
        subject = 'Your OTP for Password Reset'
        message = f'Your OTP for password reset is {otp}. It is valid for 5 minutes. Thank you.'
 
        try:
            send_mail(
                subject,
                message,
                'username',
                [username],  
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
 
    def hash_value(self, value):
        """Hash the provided value using a secure hashing algorithm."""
        return hashlib.sha256(value.encode()).hexdigest()
   
class ResetPasswordView(APIView):
    def post(self, request):
        username = request.data.get('username')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
 
 
        if not username or not new_password:
            return Response({"error": "Username and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
       
        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
     
            validate_password(new_password)
 
            hashed_username = self.hash_value(username)
            login_instance = DigiAdminLogin.objects.get(username=hashed_username)
            login_instance.password = make_password(new_password)
            login_instance.save()
 
            return Response({'success': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
 
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
 
        except DigiAdminLogin.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
 
 
    def hash_value(self, value):
        """Hash the provided value using a secure hashing algorithm."""
        return hashlib.sha256(value.encode()).hexdigest()
        
class CountDoctors(APIView):
    def get(self, request):
        try:
            total_doctors = DoctorRegister.objects.count()
            verified_doctors = DoctorRegister.objects.filter(is_verified=True).count()
            not_verified_doctors = DoctorRegister.objects.filter(is_verified=False).count()
            active_doctors = DoctorRegister.objects.filter(is_active=True).count()
            inactive_doctors = DoctorRegister.objects.filter(is_active=False).count()
 
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

class ViewDocDetails(APIView):  
    def get(self, request):
        try:
            doctor_id = request.query_params.get('doctor_id')
            if not doctor_id:
                return Response({"error": "Doctor ID is required"}, status=status.HTTP_400_BAD_REQUEST)
 
            doctor_details = PersonalsDetails.objects.filter(doctor__id=doctor_id).first()
            
            if not doctor_details:
          
                doctor_register = DoctorRegister.objects.filter(id=doctor_id).first()  
                if doctor_register:
                    mobile_number = doctor_register.mobile_number
                    is_verified = doctor_register.is_verified
                    is_active = doctor_register.is_active
                    
                    return Response({"mobile_number": mobile_number, "is_verified":is_verified, "is_active":is_active}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
 
            serializer = DoctorDetailAdmin(doctor_details)  
            return Response(serializer.data, status=status.HTTP_200_OK)
 
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self, request, format=None):
        doctor_id = request.data.get('doctor_id')
        try:
            if not doctor_id:
                return Response({'error': 'Doctor ID is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_details = PersonalsDetails.objects.filter(doctor__id=doctor_id).first()
            
            if not user_details:
                doctor_register = DoctorRegister.objects.filter(id=doctor_id).first()
                if not doctor_register:
                    return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)
 
                serializer = DoctorRegisterSerializer(doctor_register, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'success': 'Doctor Register Details Updated'}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
            serializer = DoctorDetailAdmin(user_details, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'User Details Updated'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
class ActiveDoctors(APIView):
    def get(self, request):
        # Retrieve active doctors from DoctorRegister
        active_doctors = DoctorRegister.objects.filter(is_active=True)
        active_serializer = DocDetailSerializer(active_doctors, many=True)
        active_data = {doctor['id']: doctor for doctor in active_serializer.data}

        # Retrieve related details from DoctorDetail
        inactive_doctors = PersonalsDetails.objects.filter(doctor__is_active=True)
        inactive_serializer = DocDetailforSerializer(inactive_doctors, many=True)
        inactive_data = {detail['doctor']: detail for detail in inactive_serializer.data}

        # Filter active data to exclude those present in inactive data
        filtered_active_data = {id: data for id, data in active_data.items() if id not in inactive_data}

        # Combine inactive data and filtered active data
        combined_data = list(inactive_data.values()) + list(filtered_active_data.values())

        return Response(combined_data, status=status.HTTP_200_OK)

class InactiveDoctors(APIView):
    def get(self, request):
        # Retrieve active doctors from DoctorRegister
        active_doctors = DoctorRegister.objects.filter(is_active=False)
        active_serializer = DocDetailSerializer(active_doctors, many=True)
        active_data = {doctor['id']: doctor for doctor in active_serializer.data}

        # Retrieve related details from DoctorDetail
        inactive_doctors = PersonalsDetails.objects.filter(doctor__is_active=False)
        inactive_serializer = DocDetailforSerializer(inactive_doctors, many=True)
        inactive_data = {detail['doctor']: detail for detail in inactive_serializer.data}

        # Filter active data to exclude those present in inactive data
        filtered_active_data = {id: data for id, data in active_data.items() if id not in inactive_data}

        # Combine inactive data and filtered active data
        combined_data = list(inactive_data.values()) + list(filtered_active_data.values())

        return Response(combined_data, status=status.HTTP_200_OK)
 
class VerifiedDoctors(APIView):
    def get(self, request):
        # Retrieve active doctors from DoctorRegister
        active_doctors = DoctorRegister.objects.filter(is_verified=True)
        active_serializer = DocDetailSerializer(active_doctors, many=True)
        active_data = {doctor['id']: doctor for doctor in active_serializer.data}

        # Retrieve related details from DoctorDetail
        inactive_doctors = PersonalsDetails.objects.filter(doctor__is_verified=True)
        inactive_serializer = DocDetailforSerializer(inactive_doctors, many=True)
        inactive_data = {detail['doctor']: detail for detail in inactive_serializer.data}

        # Filter active data to exclude those present in inactive data
        filtered_active_data = {id: data for id, data in active_data.items() if id not in inactive_data}

        # Combine inactive data and filtered active data
        combined_data = list(inactive_data.values()) + list(filtered_active_data.values())

        return Response(combined_data, status=status.HTTP_200_OK)
   
class UnVerifiedDoctors(APIView):
    def get(self, request):
        # Retrieve active doctors from DoctorRegister
        active_doctors = DoctorRegister.objects.filter(is_verified=False)
        active_serializer = DocDetailSerializer(active_doctors, many=True)
        active_data = {doctor['id']: doctor for doctor in active_serializer.data}

        # Retrieve related details from DoctorDetail
        inactive_doctors = PersonalsDetails.objects.filter(doctor__is_verified=False)
        inactive_serializer = DocDetailforSerializer(inactive_doctors, many=True)
        inactive_data = {detail['doctor']: detail for detail in inactive_serializer.data}

        # Filter active data to exclude those present in inactive data
        filtered_active_data = {id: data for id, data in active_data.items() if id not in inactive_data}

        # Combine inactive data and filtered active data
        combined_data = list(inactive_data.values()) + list(filtered_active_data.values())

        return Response(combined_data, status=status.HTTP_200_OK)
    
class RegisteredDoctors(APIView):
    def get(self, request):
        registered_doctors = DoctorRegister.objects.filter(is_doctor=True)
        response_data = []
 
        for doctor in registered_doctors:
            # Fetch the related DoctorDetail
            doctor_detail = doctor.details.first()  # Assuming 'details' is the related_name
 
            # Construct the data dictionary
            doctor_data = {
                'id': doctor.id,
                'name': doctor_detail.name if doctor_detail else None,
                'mobile_number': doctor.mobile_number,
                'is_verified': doctor.is_verified,
                'is_active': doctor.is_active,
                'registration_no': doctor_detail.registration_no if doctor_detail else None,
            }
           
            response_data.append(doctor_data)
 
        return Response(response_data, status=status.HTTP_200_OK)
    
    
    
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