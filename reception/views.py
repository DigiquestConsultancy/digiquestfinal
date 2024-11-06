from datetime import datetime, timezone
import logging
from clinic.models import ClinicRegister
from clinic.serializers import DoctorDetailClinicSerializer
from patient.serializers import  PatientDetailSerializerPost
from patient.models import PatientDetails, PatientRegister, PatientVarryDetails
from doctorappointment.models import Appointmentslots
from doctorappointment.serializers import BookedAppointmentSerializer, DoctorSlotSerializer
from doctor.models import DoctorDetail, DoctorRegister, PersonalsDetails
from reception.models import ReceptionDetails, ReceptionRegister
from reception.utils import generate_otp, register_otp_for_reception, send_register_otp_to_reception
from reception.serializers import AllAppointmentslotsSerializer, PostDetailSerializer, ReceptionDetailsSerializer, ReceptionRegisterSerializer
import random
import re
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q


import logging
error_reception = logging.getLogger('error_reception')
info_reception = logging.getLogger('info_reception')
warning_reception= logging.getLogger('warning_reception')



class ReceptionRegisters(APIView):
    def get(self, request, format=None):
        mobile_number = request.query_params.get("mobile_number")
        try:
            if not mobile_number:
                error_reception.error("Mobile number is required")
                return Response({"error": "Mobile number is required"}, status=status.HTTP_400_BAD_REQUEST)
            if not re.match(r"^\d{10}$", mobile_number):
                error_reception.error("Please enter a 10-digit number.")
                return Response({"error": "Please enter a 10-digit number."}, status=status.HTTP_400_BAD_REQUEST)
            if ReceptionRegister.objects.filter(mobile_number=mobile_number).exists():
                error_reception.error("Mobile number is already registered: %s", mobile_number)
                return Response({"error": "Mobile number is already registered"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if DoctorRegister.objects.filter(mobile_number=mobile_number).exists():
                    return Response({"error": 'You are already registered as a Doctor, Please try with another mobile number'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if ClinicRegister.objects.filter(mobile_number=mobile_number).exists():
                        return Response({"error":'You are already registered as a clinic, Please try with another mobile number'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                info_reception.info("Mobile number: %s", mobile_number)
                cache.set("Reception" + str(mobile_number), mobile_number, timeout=300)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # otp = ''.join(random.choices('0123456789', k=6))
            otp=generate_otp()
            register_otp_for_reception(mobile_number, otp)
            send_register_otp_to_reception(mobile_number, otp)
            print(otp)
            info_reception.info("OTP generated for mobile number %s: %s", mobile_number, otp)
            cache.set(mobile_number, otp, timeout=300)
            return Response({"success": "OTP generated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            mobile_number = request.data.get("mobile_number")
            doctor_id = request.data.get("doctor_id")
            otp = request.data.get("otp")

            if not mobile_number or not otp or not doctor_id:
                error_msg = "Mobile number, doctor_id, and OTP are required."
                error_reception.error(error_msg)
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

            if not re.match(r"^\d{10}$", mobile_number):
                error_msg = "Please enter a valid 10-digit mobile number."
                error_reception.error(error_msg)
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

            if ReceptionRegister.objects.filter(mobile_number=mobile_number).exists():
                error_msg = f"Mobile number {mobile_number} is already registered."
                error_reception.error(error_msg)
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

            cached_mobile_number = cache.get("Reception" + str(mobile_number))
            cached_otp = cache.get(mobile_number)

            if cached_mobile_number != mobile_number or cached_otp is None:
                error_msg = f"Mobile number {mobile_number} is not registered or OTP session expired. Resend OTP."
                error_reception.error(error_msg)
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

            if otp != cached_otp:
                error_msg = "Incorrect OTP. Please try again."
                error_reception.error(error_msg)
                return Response({"error": error_msg}, status=status.HTTP_400_BAD_REQUEST)

            doctor = DoctorRegister.objects.get(id=doctor_id)

            request.data["doctor"] = doctor.pk
            reception_serializer = ReceptionRegisterSerializer(data=request.data)
            if reception_serializer.is_valid():
                reception_serializer.save()
                info_reception.info(f"User with mobile number {mobile_number} successfully registered.")
                return Response({'success': "You are successfully registered!"}, status=status.HTTP_201_CREATED)
            else:
                return Response(reception_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DoctorRegister.DoesNotExist:
            error_msg = f"Doctor with id {doctor_id} does not exist."
            error_reception.error(error_msg)
            return Response({"error": error_msg}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        
        
class ReceptionDetail(APIView):
    def get(self, request, format=None):
        reception_id = request.query_params.get('reception_id')
        if not reception_id:
            return Response({"error": "id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            reception_register = ReceptionRegister.objects.filter(id=reception_id).first()
            if not reception_register:
                return Response({"error": "id not match.", "reception_id": reception_id}, status=status.HTTP_404_NOT_FOUND)
        
            mobile=reception_register.mobile_number
            reception_details = ReceptionDetails.objects.filter(reception=reception_register)
            if not reception_details.exists():
                return Response({"success": "Kindly update your details.", "reception_id": reception_id, "mobile_number":mobile}, status=status.HTTP_200_OK)
            
            serializer = ReceptionDetailsSerializer(reception_details, many=True)
            # reception_details_with_mobile = [
            #     {**detail, "reception_id": reception_id} for detail in serializer.data
            # ]
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
         
            return Response({"error": f"An error occurred while processing the request: {str(e)}", "reception_id": reception_id}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def post(self, request, format=None):
        mobile_number = request.data.get("mobile_number")
        try:
            if not mobile_number:
              
                return Response({'error': 'Mobile number is missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            
            reception_register = ReceptionRegister.objects.filter(mobile_number=mobile_number).first()
            if not reception_register:
               
                return Response({"error": "Mobile number is not Registered"}, status=status.HTTP_404_NOT_FOUND)
            
            # Create a mutable copy of the request data
            data = request.data.copy()
            data["reception"] = reception_register.pk
    
            # import pdb;pdb.set_trace()
            serializer = PostDetailSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                response_data = serializer.data
                response_data['success'] = 'Your details successfully saved'
                return Response( response_data,status=status.HTTP_201_CREATED)
            else:
              
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, format=None):
        reception_id = request.data.get('reception_id')

        if not reception_id:
            return Response({"error": "Reception ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            reception_details = ReceptionDetails.objects.get(reception__id=reception_id)
            
            
            serializer = ReceptionDetailsSerializer(reception_details, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"success":"details successfully updated","data":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except ReceptionDetails.DoesNotExist:
            return Response({"error": "Reception details not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def patch(self, request, format=None):
        reception_id = request.data.get('reception_id')

        if not reception_id:
            return Response({"error": "Reception ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            
            reception_details = ReceptionDetails.objects.get(reception__id=reception_id)
            
            
            serializer = ReceptionDetailsSerializer(reception_details, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({"success":"details successfully updated","data":serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except ReceptionDetails.DoesNotExist:
            return Response({"error": "Reception details not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, format=None):
        reception_ids = request.data.get('reception_ids', [])

        try:
            if not reception_ids:
                return Response({'error': 'reception_ids are missing in the request'}, status=status.HTTP_400_BAD_REQUEST)
            
           
            reception_details = ReceptionRegister.objects.filter(id__in=reception_ids)
            
            if not reception_details.exists():
                return Response({'error': 'No Reception details found with provided ids'}, status=status.HTTP_404_NOT_FOUND)
      
            reception_details.delete()
            
            return Response({'success': f'{len(reception_ids)} Reception Details Deleted'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ReceptionDetailsByDoctorId(APIView):
    def get(self, request):
        doctor_id = request.query_params.get('doctor_id')
        
        if not doctor_id:
            return Response({"error": "doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            registered_reception = ReceptionRegister.objects.filter(doctor_id=doctor_id)
            
            reception_with_details = ReceptionDetails.objects.filter(reception__doctor_id=doctor_id)
            
            serializer = ReceptionDetailsSerializer(reception_with_details, many=True)
            
            reception_numbers_with_details = list(reception_with_details.values_list('reception__mobile_number', flat=True))
            
            response_data = []
            
            if reception_with_details.exists():
                response_data.extend(serializer.data)

            for reception in registered_reception:
                if reception.mobile_number not in reception_numbers_with_details:
                    response_data.append({
                        "reception_id": reception.id,  
                        "mobile_number": reception.mobile_number,
                    })
                    
            if not response_data:
                    return Response({"error":"you are not register any reception"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        except ReceptionRegister.DoesNotExist:
            return Response({"error": f"Doctor with id {doctor_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

class AppointmentDetailsByReceptionID(APIView):
    def get(self, request):
        reception_id = request.query_params.get('reception_id')       
        try:
            if not reception_id:
                return Response({"error": "reception_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                reception = ReceptionRegister.objects.get(id=reception_id)
            except ReceptionRegister.DoesNotExist:
                return Response({"error": f"reception with id {reception_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
            # Get doctor_id associated with the reception
            doctor_id = reception.doctor.id
            
            # Fetch all appointment slots for the doctor
            appointment_slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, is_booked=True)
            
            if appointment_slots.exists():
                # Serialize appointment slots data
                serializer = BookedAppointmentSerializer(appointment_slots, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"No appointment slots found for Doctor {doctor_id}"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  

class BookByReception(APIView):
    def post(self, request, format=None):
        reception_id = request.data.get("reception_id")
        patient_id = request.data.get("patient_id")
        doctor_id = request.data.get("doctor_id")
        appointment_slot_id = request.data.get("appointment_slot_id")
        
        if not reception_id or not patient_id or not doctor_id or not appointment_slot_id:
            return Response({"error": "Reception ID, patient ID, doctor ID, and appointment slot ID are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            receptionist = ReceptionRegister.objects.get(id=reception_id, doctor__id=doctor_id)
        except ReceptionRegister.DoesNotExist:
            return Response({"error": "Invalid receptionist ID or receptionist is not associated with the specified doctor."}, status=status.HTTP_400_BAD_REQUEST)
        
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
 
        appointment_slot.is_booked = True
        appointment_slot.booked_by = patient
        appointment_slot.is_patient = False
        appointment_slot.save()
        
       
        # appointment_slot.is_booked = True
        # appointment_slot.booked_by = patient
        # appointment_slot.appointment_type = "walk-in" 
          
        # appointment_slot.save()
        
        serializer = DoctorSlotSerializer(appointment_slot)
        return Response({"data": serializer.data, "success": "Appointment booked successfully by reception for patient."}, status=status.HTTP_201_CREATED)
    
class ReceptionSaveddetail(APIView):
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
                return Response({'success': 'Patient details saved successfully.',"data":patient_detail_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response(patient_detail_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        
class DoctorDetailByReceptionId(APIView):
    def get(self, request):
        reception_id = request.query_params.get('reception_id')

        if not reception_id:
            return Response({"error": "reception_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reception_details = ReceptionDetails.objects.get(reception_id=reception_id)
            reception_register = reception_details.reception

            if not reception_register:
                return Response({"error": f"No reception register found for reception {reception_id}"}, status=status.HTTP_404_NOT_FOUND)

            doctor_register = reception_register.doctor

            if not doctor_register:
                return Response({"error": f"No doctor register associated with reception {reception_id}"}, status=status.HTTP_404_NOT_FOUND)

            doctor_detail, created = PersonalsDetails.objects.get_or_create(doctor=doctor_register)

            serializer = DoctorDetailClinicSerializer(doctor_detail)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except ReceptionDetails.DoesNotExist:
            return Response({"error": f"Reception with id {reception_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class RceptionSearch(APIView):
    def get(self, request):
        reception_id = request.query_params.get("reception_id")
        query = request.query_params.get("query")

        if not query or not reception_id:
            return Response({"message": "Please provide a reception_id and a query to search for patient appointments."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            clinic_details = ReceptionDetails.objects.get(reception_id=reception_id)
            doctor_id = clinic_details.reception.doctor.id
        except ReceptionDetails.DoesNotExist:
            return Response({"error": "reception details not found for the specified clinic ID."}, status=status.HTTP_404_NOT_FOUND)
        try:
            appointments = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, booked_by__isnull=False)
        except Appointmentslots.DoesNotExist:
            return Response({"error": "No booked appointments found for the specified doctor ID."}, status=status.HTTP_404_NOT_FOUND)

        appointments = appointments.filter(
            Q(booked_by__name__icontains=query) |
            Q(appointment_date__icontains=query) |
            Q(booked_by__patient__mobile_number__icontains=query) |
            Q(appointment_slot__icontains=query)|
            Q(doctor__name__icontains=query)
        )
        if not appointments.exists():
            return Response(
                {"error": "No appointments found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookedAppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    
    
class AvailableWalkInSlotsCount(APIView):
    def get(self, request, format=None):
        try:
            doctor_id = request.query_params.get('doctor_id')
            appointment_dates = request.query_params.getlist(
                'appointment_date')
 
            if not doctor_id or not appointment_dates:
                return Response({"error": "Doctor ID and Dates are required."}, status=status.HTTP_400_BAD_REQUEST)
 
            try:
                doctor = PersonalsDetails.objects.get(doctor_id=doctor_id)
            except PersonalsDetails.DoesNotExist:
                return Response({"error": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)
 
            available_walk_in_slots = Appointmentslots.objects.filter(
                doctor_id=doctor.id,
                appointment_date__in=appointment_dates,
                appointment_type='walk-in'
            )
            available_online_slots = Appointmentslots.objects.filter(
                doctor_id=doctor.id,
                appointment_date__in=appointment_dates,
                is_booked=True,
                appointment_type='online'
            )
            available_follow_up_slots = Appointmentslots.objects.filter(
                doctor_id=doctor.id,
                # appointment_date__in=appointment_dates,
                appointment_type='follow-up'
            )
 
            walk_in_count = available_walk_in_slots.count()
            online_count = available_online_slots.count()
            follow_up_count = available_follow_up_slots.count()
 
            total_appointments = Appointmentslots.objects.filter(
                doctor_id=doctor.id,
                appointment_date__in=appointment_dates
            ).count()
 
            booked_appointments = Appointmentslots.objects.filter(
                doctor_id=doctor.id,
                appointment_date__in=appointment_dates,
                is_booked=True
            ).count()
 
            canceled_appointments = Appointmentslots.objects.filter(
                doctor_id=doctor.id,
                appointment_date__in=appointment_dates,
                is_canceled=True
            ).count()
            completed_appointments = Appointmentslots.objects.filter(
                doctor_id=doctor.id,
                appointment_date__in=appointment_dates,
                is_complete=True
            ).count()
            slot_details = [
 
                {"Walk-In": walk_in_count},
                {"Online": online_count},
                {"Follow-Up": follow_up_count},
                {"Total Appointments": total_appointments},
                {"Booked Appointments": booked_appointments},
                {"Canceled Appointments": canceled_appointments},
                {"Completed Appointments": completed_appointments}]
           
            return Response(slot_details, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ShowAllAppointments(APIView):
    def get(self, request):
        reception_id = request.query_params.get('reception_id')
        doctor_id = request.query_params.get('doctor_id')
        clinic_id = request.query_params.get('clinic_id')  
        today = datetime.now().date()
 
        if not doctor_id and not reception_id and not clinic_id:
            return Response({"error": "Either reception_id, clinic_id, or doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
       
        if reception_id:
            try:
                reception = ReceptionRegister.objects.get(id=reception_id)
                doctor_id = reception.doctor.id
            except ReceptionRegister.DoesNotExist:
                return Response({"error": f"Reception with id {reception_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
       
        elif clinic_id:
            try:
                clinic = ClinicRegister.objects.get(id=clinic_id)
                doctor_id = clinic.doctor.id
            except ClinicRegister.DoesNotExist:
                return Response({"error": f"Clinic with id {clinic_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
       
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        appointments_today = Appointmentslots.objects.filter(
            doctor__doctor_id=doctor_id,
            appointment_date=today,
            is_booked=True
        )
 
        if appointments_today.exists():
            serializer = AllAppointmentslotsSerializer(appointments_today, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No appointments found for today"}, status=status.HTTP_404_NOT_FOUND)