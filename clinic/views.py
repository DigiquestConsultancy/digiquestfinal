from datetime import datetime
from django.shortcuts import get_object_or_404, render
import logging

import pytz
from clinic.models import ClinicDetails, ClinicRegister
from clinic.utils import generate_otp, register_otp_for_clinic, send_register_otp_to_clinic
from patient.models import PatientDetails, PatientRegister, PatientVarryDetails
from patient.serializers import  PatientDetailSerializerPost
from doctorappointment.models import Appointmentslots
from doctorappointment.serializers import BookedAppointmentSerializer, DoctorSlotSerializer
from reception.models import ReceptionRegister
from doctor.models import DoctorDetail, DoctorRegister, PersonalsDetails
from clinic.serializers import ClinicDetailSerializer, ClinicDetailsSerializers, ClinicRegisterSerializers, DoctorDetailClinicSerializer, PatientDetailForSearchSerializer
import random
import re
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

error_clinic = logging.getLogger('error_clinic')
info_clinic = logging.getLogger('info_clinic')
warning_clinic= logging.getLogger('warning_clinic')

# Create your views here.
class ClinicRegisters(APIView):
    
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
        
        if not mobile_number:
            error_clinic.error("Mobile number is required")
            return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not re.match(r"^\d{10}$", mobile_number):
            error_clinic.error("Please enter a 10-digit number.")
            return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
        
        if ClinicRegister.objects.filter(mobile_number=mobile_number).exists():
            error_clinic.error("Mobile number is already registered: %s", mobile_number)
            return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)
        
        if DoctorRegister.objects.filter(mobile_number=mobile_number).exists():
            return Response({"error": "You are already registered as a Doctor. Please try with another mobile number"}, status=status.HTTP_400_BAD_REQUEST)
        
        if ReceptionRegister.objects.filter(mobile_number=mobile_number).exists():
            return Response({"error": "You are already registered as a reception. Please try with another mobile number"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            info_clinic.info("Mobile number: %s", mobile_number)
            cache.set("Clinic" + str(mobile_number), mobile_number, timeout=300)
            
            otp= generate_otp()
            register_otp_for_clinic(mobile_number, otp)
            send_register_otp_to_clinic(mobile_number, otp)
            info_clinic.info("OTP generated for mobile number %s: %s", mobile_number, otp)
            cache.set(mobile_number, otp, timeout=300)
            
            return Response({"success": "OTP generated successfully"}, status=status.HTTP_200_OK)
        
        except Exception as e:
            error_clinic.error("Error generating OTP: %s", str(e))
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        doctor_id = request.data.get("doctor_id")
        otp = request.data.get("otp")

        if not mobile_number or not otp or not doctor_id:
            error_msg = "Mobile number, doctor_id, and OTP are required."
            error_clinic.error(error_msg)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        if not re.match(r"^\d{10}$", mobile_number):
            error_msg = "Please enter a valid 10-digit mobile number."
            error_clinic.error(error_msg)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        if ClinicRegister.objects.filter(mobile_number=mobile_number).exists():
            error_msg = f"Mobile number {mobile_number} is already registered."
            error_clinic.error(error_msg)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        cached_mobile_number = cache.get("Clinic" + str(mobile_number))
        cached_otp = cache.get(mobile_number)

        if cached_mobile_number != mobile_number or cached_otp is None:
            error_msg = f"Mobile number {mobile_number} is not registered or OTP session expired. Resend OTP."
            error_clinic.error(error_msg)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        if otp != cached_otp:
            error_msg = "Incorrect OTP. Please try again."
            error_clinic.error(error_msg)
            return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            doctor = DoctorRegister.objects.get(id=doctor_id)
        except DoctorRegister.DoesNotExist:
            error_msg = f"Doctor with id {doctor_id} does not exist."
            error_clinic.error(error_msg)
            return Response({"error": error_msg}, status=status.HTTP_404_NOT_FOUND)
        
        request.data["doctor"] = doctor.pk
        clinic_serializer = ClinicRegisterSerializers(data=request.data)
        
        if clinic_serializer.is_valid():
            clinic_serializer.save()
            info_clinic.info(f"User with mobile number {mobile_number} successfully registered.")
            return Response({'success': "You are successfully registered!"}, status=status.HTTP_201_CREATED)
        
        return Response(clinic_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ClinicDetail(APIView):
    def get(self, request, format=None):
        clinic_id = request.query_params.get('clinic_id')
        if not clinic_id:
            return Response({"error": "clinic_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:            
            clinic = ClinicRegister.objects.get(id=clinic_id)
            mobile= clinic.mobile_number
            clinic_details = ClinicDetails.objects.filter(clinic_id=clinic_id)
            if not clinic_details.exists():
                return Response({"success": 'kindly update your details', "clinic_id": clinic_id, "mobile_number": mobile}, status=status.HTTP_200_OK)
            serializer = ClinicDetailsSerializers(clinic_details, many=True)
            return Response(serializer.data)
        except Exception as e:
            error_clinic.error(f"Error occurred while processing GET request: {e}")
            return Response({"error": f"An error occurred while processing the request: {str(e)}", "clinic_id": clinic_id}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        try:
            if not mobile_number:
                error_clinic.error('Mobile number is missing in the request')
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            
            clinic_register = ClinicRegister.objects.filter(mobile_number=mobile_number).first()
            if not clinic_register:
                error_clinic.error('Mobile number %s is not Registered', mobile_number)
                return Response({"error": "Mobile number is not Registered"}, status=status.HTTP_404_NOT_FOUND)
            
            existing_doctor_detail = ClinicDetails.objects.filter(clinic__mobile_number=mobile_number).first()
            if existing_doctor_detail:
                error_clinic.error('User details already exist for %s mobile number', mobile_number)
                return Response({"error": "Clinic details already exist for this mobile number"}, status=status.HTTP_400_BAD_REQUEST)
            
            data = request.data.copy()
            data["clinic"] = clinic_register.pk
            serializer = ClinicDetailSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                info_clinic.info('Doctor details saved successfully')
                response_data = serializer.data
                response_data['success'] = 'Your details successfully saved'
                return Response( response_data,status=status.HTTP_201_CREATED)
            else:
                error_clinic.error(f'Invalid data: {serializer.errors}')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, format=None):
        clinic_id = request.data.get('clinic_id')

        if not clinic_id:
            return Response({"error": "clinic ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:   
            clinic_details = ClinicDetails.objects.get(clinic_id=clinic_id)

            serializer = ClinicDetailSerializer(clinic_details, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"success":"details successfully updated","data":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ClinicDetails.DoesNotExist:
            return Response({"error": "clinic details not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self, request, format=None):
        
        clinic_id = request.data.get('clinic_id')
        try:
            if not clinic_id:
                return Response({'error': 'clinic id is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                
                user_details = ClinicDetails.objects.get(id=clinic_id)
            except Exception as e:
                return Response({'error': 'User details not found'}, status=status.HTTP_404_NOT_FOUND)        
            serializer = ClinicDetailSerializer(user_details, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': 'User Details Updated'},status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    def delete(self, request, format=None):
        clinic_ids = request.data.get('clinic_ids', [])

        try:
            if not clinic_ids:
                return Response({'error': 'clinic_ids are missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            
           
            clinic_details = ClinicRegister.objects.filter(id__in=clinic_ids)
            
            if not clinic_details.exists():
                return Response({'error': 'No Clinic details found with provided ids'}, status=status.HTTP_404_NOT_FOUND)
      
            clinic_details.delete()
            
            return Response({'success': f'{len(clinic_ids)} Clinic Details Deleted'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        
        
class AppointmentDetailsByClinicID(APIView):
    def get(self, request):
        clinic_id = request.query_params.get('clinic_id')
        try:
            if not clinic_id:
                return Response({"error": "clinic_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                clinic = ClinicRegister.objects.get(id=clinic_id)
            except ClinicRegister.DoesNotExist:
                return Response({"error": f"Clinic with id {clinic_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            doctor_id = clinic.doctor.id
            appointment_slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, is_booked=True)
            if appointment_slots.exists():
                serializer = BookedAppointmentSerializer(appointment_slots, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"No appointment slots found for Doctor {doctor_id}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

class PatientDetailsByClinic(APIView):
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

            patient_register_instance = PatientRegister.objects.filter(
                mobile_number=mobile_number).first()

            if patient_register_instance:
                return Response({'error': 'Patient with this mobile number already exists.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create new PatientRegister instance
            patient_register_instance = PatientRegister.objects.create(
                mobile_number=mobile_number)

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

            patient_detail_serializer = PatientDetailSerializerPost(
                data=patient_detail_data)

            if patient_detail_serializer.is_valid():
                patient_detail_serializer.save()
                return Response({'success': 'Patient details created successfully.','data':patient_detail_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(patient_detail_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class ClinicByDoctorId(APIView):
    def get(self, request):
        doctor_id = request.query_params.get('doctor_id')
        
        if not doctor_id:
            return Response({"error": "doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            registered_clinics = ClinicRegister.objects.filter(doctor_id=doctor_id)
            
            clinics_with_details = ClinicDetails.objects.filter(clinic__doctor_id=doctor_id)
            
            serializer = ClinicDetailsSerializers(clinics_with_details, many=True)
            
            clinic_numbers_with_details = list(clinics_with_details.values_list('clinic__mobile_number', flat=True))
            
            response_data = []
            
            if clinics_with_details.exists():
                response_data.extend(serializer.data)
            for clinic in registered_clinics:
                if clinic.mobile_number not in clinic_numbers_with_details:
                    response_data.append({
                        "clinic_id": clinic.id,  
                        "mobile_number": clinic.mobile_number,
                    })
                    
                if not response_data:
                    return Response({"error":"you are not register any clinic"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ClinicRegister.DoesNotExist:
            return Response({"error": f"Doctor with id {doctor_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DoctorDetailByClinicId(APIView):
    def get(self, request):
        clinic_id = request.query_params.get('clinic_id')

        if not clinic_id:
            return Response({"error": "clinic_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clinic_details = ClinicDetails.objects.get(clinic_id=clinic_id)
        except ClinicDetails.DoesNotExist:
            return Response({"error": f"Clinic with id {clinic_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        clinic_register = clinic_details.clinic

        if not clinic_register:
            return Response({"error": f"No clinic register found for clinic {clinic_id}"}, status=status.HTTP_404_NOT_FOUND)

        doctor_register = clinic_register.doctor

        if not doctor_register:
            return Response({"error": f"No doctor register associated with clinic {clinic_id}"}, status=status.HTTP_404_NOT_FOUND)

        doctor_detail, created = PersonalsDetails.objects.get_or_create(
            doctor=doctor_register)

        serializer = DoctorDetailClinicSerializer(doctor_detail)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class BookpAppointmentByClinic(APIView):
    def post(self, request, format=None):
        clinic_id = request.data.get("clinic_id")
        patient_id = request.data.get("patient_id")
        doctor_id = request.data.get("doctor_id")
        appointment_slot_id = request.data.get("appointment_slot_id")
        
        if not clinic_id or not patient_id or not doctor_id or not appointment_slot_id:
            print(request.data)
            return Response({"error": "Clinic ID, patient ID, doctor ID, and appointment slot ID are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            clinic = ClinicDetails.objects.get(clinic_id=clinic_id)
        except ClinicDetails.DoesNotExist:
            return Response({"error": "Invalid clinic ID."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = PatientVarryDetails.objects.get(id=patient_id)
        except PatientVarryDetails.DoesNotExist:
            return Response({"error": "Invalid patient ID."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            appointment_slot = Appointmentslots.objects.select_related('doctor').get(id=appointment_slot_id, doctor__doctor_id=doctor_id)
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
 
        appointment_slot.booked_by = patient
        appointment_slot.is_booked = True
        appointment_slot.save()
        
        # appointment_slot.booked_by=patient
        # appointment_slot.is_booked = True
        # appointment_slot.appointment_type = "walk-in"
        
        # appointment_slot.save()
        
        serializer = DoctorSlotSerializer(appointment_slot)
        return Response({"data": serializer.data, "success": "Appointment booked successfully by Clinic for patient."}, status=status.HTTP_201_CREATED)


class SearchClinic(APIView):
    def get(self, request):
        clinic_id = request.query_params.get("clinic_id")
        query = request.query_params.get("query")

        if not query or not clinic_id:
            return Response({"message": "Please provide a clinic_id and a query to search for patient appointments."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            clinic_details = ClinicDetails.objects.get(clinic_id=clinic_id)
            doctor_id = clinic_details.clinic.doctor.id
        except ClinicDetails.DoesNotExist:
            return Response({"error": "Clinic details not found for the specified clinic ID."}, status=status.HTTP_404_NOT_FOUND)
        try:
            appointments = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, booked_by__isnull=False)
        except Appointmentslots.DoesNotExist:
            return Response({"error": "No booked appointments found for the specified doctor ID."}, status=status.HTTP_404_NOT_FOUND)

        appointments = appointments.filter(
            Q(booked_by__name__icontains=query) |
            Q(appointment_date__icontains=query) |
            Q(booked_by__patient__mobile_number__icontains=query) |
            Q(appointment_slot__icontains=query) |
            Q(doctor__name__icontains=query)
        )
        if not appointments.exists():
            return Response(
                {"error": "No appointments found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookedAppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class SearchPatient(APIView):
    def get(self, request):
        query = request.query_params.get("query", None)
        
        if query:
            filter_by_name = Q(name__icontains=query)
            filter_by_mobile_number = Q(patient__mobile_number__icontains=query)
            doctors = PatientVarryDetails.objects.filter(
                filter_by_name | 
                filter_by_mobile_number
            )
            if not doctors.exists():
                return Response({"error": "No patient found matching the query."},status=status.HTTP_404_NOT_FOUND )
            serializer = PatientDetailForSearchSerializer(doctors, many=True)
            return Response(serializer.data)
        else:
            return Response({"error": "Please enter a query to search for doctors."},status=status.HTTP_400_BAD_REQUEST)
    
class CountAvailableSlots(APIView):
    def get(self, request):
        try:
            doctor_id = request.query_params.get("doctor_id")
            dates_str = request.query_params.getlist("dates")  
           
            if not doctor_id or not dates_str:
                return Response({"error": "Doctor ID and dates are required."}, status=status.HTTP_400_BAD_REQUEST)

            available_slots_count = []  
            ist = pytz.timezone('Asia/Kolkata')  # Set timezone to IST
            current_time = datetime.now(ist).time()  # Get current time in IST
            today_date = datetime.now(ist).date()  # Get today's date

            for date_str in dates_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    if date == today_date:
                        # Count only slots after the current time for today
                        count = Appointmentslots.objects.filter(
                            doctor__doctor_id=doctor_id,
                            appointment_date=date,
                            appointment_slot__gt=current_time,
                            is_booked=False,
                            is_blocked=False
                        ).count()
                    else:
                        # Count all slots for tomorrow and the day after tomorrow
                        count = Appointmentslots.objects.filter(
                            doctor__doctor_id=doctor_id,
                            appointment_date=date,
                            is_booked=False,
                            is_blocked=False
                        ).count()
                   
                    available_slots_count.append({"date": date_str, "count": count})
                except ValueError:
                    return Response({"error": f"Incorrect date format for {date_str}. Please provide date in YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)

            return Response(available_slots_count, status=status.HTTP_200_OK)
       
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)