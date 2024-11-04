from datetime import datetime
from django.shortcuts import render
from django.utils.timezone import make_aware
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .utils import send_meeting_link
from patient.serializers import MyAppointmentSerializer, PatientDetailSerializer
from patientappointment.serializers import AppointmentMinimalSerializer, PatientSlotSerializer
from doctor.models import DoctorDetail, DoctorRegister, PersonalsDetails
from doctorappointment.models import Appointmentslots
from doctorappointment.serializers import DoctorSlotSerializer
from patient.models import PatientDetails, PatientVarryDetails 
from django.db.models import Q

import logging
error_patientappointment = logging.getLogger('error_patientappointment')
info_patientappointment = logging.getLogger('info_patientappointment')
warning_patientappointment = logging.getLogger('warning_patientappointment')



class BookSlotListView(APIView):
    def get(self, request):
        patient_id = request.query_params.get('patient_id')
        slot_date_str = request.query_params.get('slot_date')
        if not patient_id:
            return Response({"error": "patient_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            queryset = Appointmentslots.objects.filter(booked_by_id=patient_id, is_booked=True)
            if slot_date_str:
                try:
                    slot_date = make_aware(datetime.strptime(slot_date_str, '%Y-%m-%d'))
                    queryset = queryset.filter(appointment_date=slot_date)
                except ValueError:
                    return Response({"error": "Invalid slot_date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.select_related('booked_by', 'doctor')
            slot_data = []
            for slot in queryset:
                doctor_name = slot.doctor.name if slot.doctor else ""
                doctor_specialization = slot.doctor.specialization if slot.doctor else ""
                consultation_type=slot.consultation_type if slot.consultation_type else ""
                slot_data.append({'id': slot.id,'appointment_date': slot.appointment_date,'appointment_slot': slot.appointment_slot,'doctor_name': doctor_name,'doctor_specialization': doctor_specialization,'consultation_type': consultation_type})
            if slot_data:
                return Response(slot_data, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No slot bookings found for the specified patient and date."},
                                status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
        
        
    def post(self, request, format=None):
        patient_id = request.data.get("patient")
        doctor_id = request.data.get("doctor")
        appointment_slot_id = request.data.get("appointment_slot")
        consultation_type=request.data.get("consultation_type")
        if not patient_id or not doctor_id or not appointment_slot_id or not consultation_type:
            return Response({"error": "Patient ID, doctor ID, and appointment slot ID  and consultation_type are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            patient = PatientVarryDetails.objects.get(id=patient_id)
        except PatientVarryDetails.DoesNotExist:
            return Response({"error": "Invalid patient ID."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doctor = PersonalsDetails.objects.get(doctor_id=doctor_id)
        except DoctorDetail.DoesNotExist:
            return Response({"error": "Invalid doctor ID."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            appointment_slot = Appointmentslots.objects.get(pk=appointment_slot_id, doctor__doctor_id=doctor_id)
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
            appointment_slot.appointment_type = "online"
 
        appointment_slot.is_booked = True
        appointment_slot.booked_by = patient
        appointment_slot.is_patient = True
        appointment_slot.consultation_type = consultation_type 
        appointment_slot.save()
        if consultation_type == "online":
                appointment_time = appointment_slot.appointment_slot.strftime("%H:%M:%S")
                email_sent = send_meeting_link(doctor.email,appointment_time)
                email_sent = send_meeting_link(patient.email,appointment_time)
                if not email_sent:
                    return Response({"error": "Failed to send email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = DoctorSlotSerializer(appointment_slot)
        return Response({"success": "Slot confirmed successfully.","data": serializer.data,},status=status.HTTP_201_CREATED)
    
    
# ==============for particular field===================
class PatientSlotView(APIView):
    def get(self, request):
        patient_id = request.query_params.get('patient_id')
        doctor_id = request.query_params.get('doctor_id')
        
        if not patient_id:
            return Response({"error": "patient_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Appointmentslots.objects.filter(booked_by__patient_id=patient_id, is_booked=True)
        
        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        try:
            if doctor_id:
                serializer = AppointmentMinimalSerializer(queryset, many=True)
            else:
                serializer = PatientSlotSerializer(queryset, many=True)
            
            return Response({"success": "appointmentslot", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        patient_id = request.data.get('patient_id')
        slot_id = request.data.get('slot_id')  

        if not patient_id or not slot_id:
            return Response({"error": "patient_id and slot_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            slot = Appointmentslots.objects.get(id=slot_id, booked_by_id__patient_id=patient_id, is_booked=True)
            slot.booked_by = None
            slot.is_booked = False
            slot.save()

            return Response({"success": "Appointment slot cancelled successfully"}, status=status.HTTP_200_OK)

        except Appointmentslots.DoesNotExist:
            return Response({"error": "Appointment slot not found or not booked by the patient"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request):
        try:
            patient_id = request.data.get('patient_id')
            slot_id = request.data.get('slot_id')

            if not patient_id or not slot_id:
                return Response({"error": "Both patient_id and slot_id are required"}, status=status.HTTP_400_BAD_REQUEST)

            # Retrieve the slot and associated patient
            slot = Appointmentslots.objects.get(id=slot_id, booked_by_id__patient_id=patient_id, is_booked=True)

            # Update fields if provided in request data
            if 'patient_name' in request.data:
                slot.booked_by.name = request.data['patient_name']
                slot.booked_by.save()

            if 'slot_time' in request.data:
                slot.slot_time = request.data['slot_time']
                slot.save()

            return Response({"success": "Appointment slot updated successfully"}, status=status.HTTP_200_OK)

        except Appointmentslots.DoesNotExist:
            return Response({"error": "Appointment slot not found or not booked"}, status=status.HTTP_404_NOT_FOUND)

        except DoctorDetail.DoesNotExist:
            return Response({"error": "Doctor with specified ID does not exist"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SlotDetailsBySlotId(APIView):

    def get(self, request):
        patient_id = request.query_params.get('patient_id')
        slot_id = request.query_params.get('slot_id')

        if not patient_id or not slot_id:
            return Response({"error": "patient_id and slot_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch patient details
            patient = PatientDetails.objects.get(id=patient_id)

            # Fetch all appointment slots for the patient matching slot_id and is_booked=True
            queryset = Appointmentslots.objects.filter(booked_by_id=patient_id, id=slot_id, is_booked=True)

            # Serialize patient details and appointment slots
            PatientDetailsSerializer = PatientDetailSerializer(patient)
            SlotDetails = PatientSlotSerializer(queryset, many=True)

            return Response({
                "success": "appointmentslot",
                "patient_details": (PatientDetailsSerializer.data,
                SlotDetails.data)
            }, status=status.HTTP_200_OK)

        except PatientDetails.DoesNotExist:
           
            return Response({"error": "Patient does not exist"}, status=status.HTTP_404_NOT_FOUND)

        except Appointmentslots.DoesNotExist:
  
            return Response({"error": "Appointment slot does not exist"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
 
            return Response({"error": "Failed to retrieve data"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SearchMyAppointments(APIView):
    def get(self, request):
        try:
            query = request.query_params.get("query", None)
            patient_id = request.query_params.get("patient_id", None)
           
            if not patient_id:
                return Response({"error": "Please provide a patient_id to retrieve appointments."}, status=status.HTTP_400_BAD_REQUEST)
           
            appointments = Appointmentslots.objects.filter(booked_by__patient_id=patient_id)
           
            if not appointments.exists():
                return Response({"error": "No appointments found for the given patient_id."}, status=status.HTTP_404_NOT_FOUND)
           
            if query:
                filter_by_patient_name = Q(booked_by__name__icontains=query)
                filter_by_specialization = Q(doctor__specialization__icontains=query)
                filter_by_appointment_date = Q(appointment_date__icontains=query)
                filter_by_doctor_name = Q(doctor__name__icontains=query)
                filter_by_mobile_number = Q(doctor__doctor__mobile_number__icontains=query)
               
                filtered_appointments = appointments.filter(
                    filter_by_patient_name | filter_by_specialization| filter_by_appointment_date | filter_by_doctor_name | filter_by_mobile_number
                )
               
                if not filtered_appointments.exists():
                    return Response({"error": "No appointments found."}, status=status.HTTP_404_NOT_FOUND)
               
                appointments = filtered_appointments
           
            serializer = MyAppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
       
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        