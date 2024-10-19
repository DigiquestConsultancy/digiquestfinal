from datetime import date, datetime, timedelta, timezone
from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.views import APIView
from django.conf import settings
from patient.serializers import PatientDetailSerializer
from patient.models import PatientDetails
from doctor.models import DoctorDetail, PersonalsDetails
from .serializers import AppointmentslotsSerializer, DoctorSlotSerializer
from doctorappointment.models import Appointmentslots
from doctorappointment.serializers import BookedAppointmentSerializer
from django.db.models import Q
from django.core.mail import send_mail



import logging
error_doctorappointment = logging.getLogger('error_doctorappointment')
info_doctorappointment = logging.getLogger('info_doctorappointment')
warning_doctorappointment = logging.getLogger('warning_doctorappointment')


class DoctorSlotCreate(APIView):
    def get(self, request):
        try:
            doctor_id = request.query_params.get('doctor_id')
            slot_id = request.query_params.get('slot_id')
            slot_date_str = request.query_params.get('slot_date')
            
            if not doctor_id:
                return Response({"error": "doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                if slot_id and slot_date_str:
                    slot_date = datetime.strptime(slot_date_str, '%Y-%m-%d').date()
                    slot = Appointmentslots.objects.get(pk=slot_id, doctor__doctor_id=doctor_id)
                    if slot.appointment_date != slot_date:
                        return Response({"error": "Slot ID and date do not match"}, status=status.HTTP_400_BAD_REQUEST)
                    serializer = DoctorSlotSerializer(slot)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                elif slot_id:
                    slot = Appointmentslots.objects.get(pk=slot_id, doctor__doctor_id=doctor_id)
                    serializer = DoctorSlotSerializer(slot)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                elif slot_date_str:
                    slot_date = datetime.strptime(slot_date_str, '%Y-%m-%d').date()
                    slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, appointment_date=slot_date).order_by('appointment_slot')
                    if not slots.exists():
                        return Response({"error": "No slots available for the given date"}, status=status.HTTP_404_NOT_FOUND)
                    serializer = DoctorSlotSerializer(slots, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                
                else:
                    slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id)
                    serializer = DoctorSlotSerializer(slots, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointmentslots.DoesNotExist:
                return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return Response({"error": "Invalid date format. Please provide slot_date in 'YYYY-MM-DD' format"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
         
    def post(self, request):
        try:
            doctor_id = request.data.get("doctor_id")
            start_date_str = request.data.get('start_date')
            start_time_str = request.data.get('start_time')
            end_date_str = request.data.get('end_date')
            end_time_str = request.data.get('end_time')
            interval_minutes = int(request.data.get('interval_minutes'))
            leave_dates = request.data.get('leave_dates', [])
            
            if not all([doctor_id, start_date_str, start_time_str, end_date_str, end_time_str, interval_minutes]):
                return Response({"error": "doctor_id, start_date, start_time, end_date, interval_minutes, and end_time are required"}, status=status.HTTP_400_BAD_REQUEST)
            
            existing_doctor_detail = PersonalsDetails.objects.filter(doctor_id=doctor_id).first()
            if not existing_doctor_detail:
                return Response({"error": f"Doctor details not found for ID: {doctor_id}"}, status=status.HTTP_404_NOT_FOUND)
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            
            if end_date < start_date or (end_date == start_date and end_time <= start_time):
                return Response({"error": "End datetime must be after start datetime"}, status=status.HTTP_400_BAD_REQUEST)
            
            current_date = start_date
            while current_date <= end_date:
                if str(current_date.date()) not in leave_dates:
                    current_time = datetime.combine(current_date, start_time)
                    end_slot_datetime = datetime.combine(current_date, end_time)
                    while current_time < end_slot_datetime:
                        if Appointmentslots.objects.filter(
                            doctor=existing_doctor_detail,
                            appointment_date=current_time.date(),
                            appointment_slot=current_time.time()
                        ).exists():
                            return Response({"error": "Slot already created for the given datetime range"}, status=status.HTTP_400_BAD_REQUEST)
                        Appointmentslots.objects.create(
                            doctor=existing_doctor_detail,  
                            appointment_date=current_time.date(),
                            appointment_slot=current_time.time(),
                            is_booked=False
                        )
                        current_time += timedelta(minutes=interval_minutes)
                
                current_date += timedelta(days=1)
            
            return Response({"success": "Doctor slots created successfully"}, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   
    def patch(self, request):
        doctor_id = request.data.get("doctor_id")
        start_date_str = request.data.get('start_date')
        start_time_str = request.data.get('start_time')
        end_date_str = request.data.get('end_date')
        end_time_str = request.data.get('end_time')
 
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            doctor = PersonalsDetails.objects.get(id=doctor_id)
        except DoctorDetail.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            start_date = datetime.strptime(
                start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(
                end_date_str, '%Y-%m-%d').date() if end_date_str else None
            start_time = datetime.strptime(
                start_time_str, '%H:%M').time() if start_time_str else None
            end_time = datetime.strptime(
                end_time_str, '%H:%M').time() if end_time_str else None
        except ValueError:
            return Response({"error": "Invalid date or time format"}, status=status.HTTP_400_BAD_REQUEST)
 
        if start_date and end_date and start_date > end_date:
            return Response({"error": "End date must be after start date"}, status=status.HTTP_400_BAD_REQUEST)
        if start_time and end_time and start_date == end_date and start_time > end_time:
            return Response({"error": "End time must be after start time on the same date"}, status=status.HTTP_400_BAD_REQUEST)
 
        blocked_slots = []
 
 
        current_date = start_date if start_date else end_date
        end_date = end_date if end_date else start_date
 
        while current_date <= end_date:
            current_time = datetime.combine(
                current_date, start_time) if start_time else datetime.min.time()
            end_time_combined = datetime.combine(
                current_date, end_time) if end_time else datetime.max.time()
 
            slots = Appointmentslots.objects.filter(
                doctor=doctor,
                appointment_date=current_date,
                appointment_slot__gte=current_time,
                appointment_slot__lte=end_time_combined
            )
 
            for slot in slots:
                if not slot.is_booked:
                    # return Response({"error": f"Slot on {current_date} at {slot.appointment_slot.strftime('%H:%M')} is already booked and cannot be blocked"}, status=status.HTTP_400_BAD_REQUEST)
                    slot.is_blocked = True
                    slot.save()
                    blocked_slots.append({
                        'appointment_date': slot.appointment_date,
                        'appointment_slot': slot.appointment_slot.strftime('%H:%M'),
                        'is_blocked': slot.is_blocked
                    })
 
                current_date += timedelta(days=1)
 
            return Response({"success": "Available slots have been blocked successfully", 'blocked_slots': blocked_slots}, status=status.HTTP_200_OK)        

   

class UnblockSlots(APIView):
    def patch(self, request):
        doctor_id = request.data.get("doctor_id")
        start_date_str = request.data.get('start_date')
        start_time_str = request.data.get('start_time')
        end_date_str = request.data.get('end_date')
        end_time_str = request.data.get('end_time')
 
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            doctor = PersonalsDetails.objects.get(id=doctor_id)
        except DoctorDetail.DoesNotExist:
            return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            start_date = datetime.strptime(
                start_date_str, '%Y-%m-%d').date() if start_date_str else None
            end_date = datetime.strptime(
                end_date_str, '%Y-%m-%d').date() if end_date_str else None
            start_time = datetime.strptime(
                start_time_str, '%H:%M').time() if start_time_str else None
            end_time = datetime.strptime(
                end_time_str, '%H:%M').time() if end_time_str else None
        except ValueError:
            return Response({"error": "Invalid date or time format"}, status=status.HTTP_400_BAD_REQUEST)
 
        if start_date and end_date and start_date > end_date:
            return Response({"error": "End date must be after start date"}, status=status.HTTP_400_BAD_REQUEST)
        if start_time and end_time and start_date == end_date and start_time > end_time:
            return Response({"error": "End time must be after start time on the same date"}, status=status.HTTP_400_BAD_REQUEST)
 
        unblocked_slots = []
 
 
        current_date = start_date if start_date else end_date
        end_date = end_date if end_date else start_date
 
        while current_date <= end_date:
            current_time = datetime.combine(
                current_date, start_time) if start_time else datetime.min.time()
            end_time_combined = datetime.combine(
                current_date, end_time) if end_time else datetime.max.time()
 
            slots = Appointmentslots.objects.filter(
                doctor=doctor,
                appointment_date=current_date,
                appointment_slot__gte=current_time,
                appointment_slot__lte=end_time_combined
            )
 
            for slot in slots:
                slot.is_blocked = False
                slot.save()
                unblocked_slots.append({
                    'appointment_date': slot.appointment_date,
                    'appointment_slot': slot.appointment_slot.strftime('%H:%M'),
                    'is_blocked': slot.is_blocked
                })
 
            current_date += timedelta(days=1)
 
        return Response({"success": "Slots have been unblocked successfully", 'unblocked_slots': unblocked_slots}, status=status.HTTP_200_OK)        
 

class TodayAndAfterTodaySlot(APIView):
    
    def get(self, request):
        try:
            doctor_id = request.query_params.get('doctor_id')
            today = datetime.now().date()

            slots = Appointmentslots.objects.select_related('doctor', 'booked_by__patient').filter(
                doctor_id=doctor_id,
                appointment_date__gte=today
            ).order_by('appointment_date','appointment_slot')

            serialized_slots = DoctorSlotSerializer(slots, many=True)

            return Response(serialized_slots.data)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CurrentDateSlot(APIView):
    def get(self, request):
        try:
            doctor_id = request.query_params.get('doctor_id')
            if not doctor_id:
                return Response({"error": "doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            current_date = datetime.now().date()
            try:
                slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, appointment_date=current_date).order_by('appointment_slot')
                if not slots.exists():
                    return Response({"error": "No slots found for the current date"}, status=status.HTTP_404_NOT_FOUND)
                serializer = DoctorSlotSerializer(slots, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointmentslots.DoesNotExist:
                return Response({"error": "No slots found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
       
class BookedAppointments(APIView):
    def get(self, request):
        try:
            doctor_id = request.query_params.get('doctor_id')
            if not doctor_id:
                return Response({"error":"doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            appointments = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, is_booked=True).order_by('-appointment_date', '-appointment_slot')
            serializer = BookedAppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    def patch(self, request):
        try:
            appointment_id = request.data.get('appointment_id')
            
            if not appointment_id:
                return Response({"error": "appointment_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            appointment = Appointmentslots.objects.get(id=appointment_id)
            appointment.booked_by = None
            appointment.is_booked = False
            appointment.save()

            return Response({"success": "Appointment slot has been freed up successfully"}, status=status.HTTP_200_OK)
        
        except Appointmentslots.DoesNotExist:
            return Response({"error": "Appointment slot not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request):
        try:
            appointment_id = request.data.get('appointment_id')
            
            if not appointment_id:
                return Response({"error": "appointment_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            appointment = Appointmentslots.objects.get(id=appointment_id)
            appointment.delete()

            return Response({"success": "Appointment slot has been deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        
        except Appointmentslots.DoesNotExist:
            return Response({"error": "Appointment slot not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

   
class PatientDetailUpdateByDoctor(APIView):
    def patch(self, request):
        try:
            appointment_id = request.data.get('appointment_id')
            patient_id = request.data.get('patient_id')

            if not appointment_id or not patient_id:
                return Response({"error": "appointment_id and patient_id parameters are required"}, status=status.HTTP_400_BAD_REQUEST)
        
            appointment = Appointmentslots.objects.get(id=appointment_id)
            patient = PatientDetails.objects.get(id=patient_id) 

            if appointment.booked_by.id != patient_id:
                return Response({"error": "Appointment ID and Patient ID do not match"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = PatientDetailSerializer(patient, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                appointment.patient = patient
                appointment.is_booked = True
                appointment.save()

                return Response({"message": "Appointment slot and patient details have been updated successfully"})
        
            return Response(serializer.errors)
    
        except Appointmentslots.DoesNotExist:
            return Response({"error": "Appointment slot not found"})
    
        except PatientDetails.DoesNotExist:
            return Response({"error": "Booked by patient not found"})
    
        except Exception as e:
            return Response({"error": str(e)})


class SlotGetByPatient(APIView):
    def get(self, request):
        try:
            doctor_id = request.query_params.get('doctor_id')
            slot_id = request.query_params.get('slot_id')
            slot_date_str = request.query_params.get('slot_date')
            if not doctor_id:
                return Response({"error": "doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                if slot_id and slot_date_str:
                    slot_date = datetime.strptime(slot_date_str, '%Y-%m-%d').date()
                    slot = Appointmentslots.objects.get(pk=slot_id, doctor__doctor_id=doctor_id, is_booked=False,is_blocked=False)
                    if slot.appointment_date != slot_date:
                        return Response({"error": "Slot ID and date do not match"}, status=status.HTTP_400_BAD_REQUEST)
                    serializer = DoctorSlotSerializer(slot)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                elif slot_id:
                    slot = Appointmentslots.objects.get(pk=slot_id, doctor__doctor_id=doctor_id , is_booked=False,is_blocked=False)
                    serializer = DoctorSlotSerializer(slot)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                elif slot_date_str:
                    slot_date = datetime.strptime(slot_date_str, '%Y-%m-%d').date()
                    slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, appointment_date=slot_date, is_booked=False,is_blocked=False)
                    serializer = DoctorSlotSerializer(slots, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, is_booked=False, is_blocked=False)
                    serializer = DoctorSlotSerializer(slots, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            except Appointmentslots.DoesNotExist:
                return Response({"error": "Slot not found"}, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return Response({"error": "Invalid date format. Please provide slot_date in 'YYYY-MM-DD' format"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    # def get(self, request):
    #     try:
    #         doctor_id = request.query_params.get('doctor_id')
    #         slot_id = request.query_params.get('slot_id')
    #         slot_date_str = request.query_params.get('slot_date')
    #         if not doctor_id:
    #             return Response({"error": "doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            
    #         try:
    #             if slot_id and slot_date_str:
    #                 slot_date = datetime.strptime(slot_date_str, '%Y-%m-%d').date()
    #                 slot = Appointmentslots.objects.get(pk=slot_id, doctor__doctor_id=doctor_id, is_booked=False, is_blocked=False)
    #                 if slot.appointment_date != slot_date:
    #                     return Response({"error": "Slot ID and date do not match"}, status=status.HTTP_400_BAD_REQUEST)
    #                 serializer = DoctorSlotSerializer(slot)
    #                 return Response(serializer.data, status=status.HTTP_200_OK)
    #             elif slot_id:
    #                 slot = Appointmentslots.objects.get(pk=slot_id, doctor__doctor_id=doctor_id, is_booked=False, is_blocked=False)
    #                 serializer = DoctorSlotSerializer(slot)
    #                 return Response(serializer.data, status=status.HTTP_200_OK)
    #             elif slot_date_str:
    #                 slot_date = datetime.strptime(slot_date_str, '%Y-%m-%d').date()
    #                 slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, appointment_date=slot_date, is_booked=False, is_blocked=False)
    #                 if slots.exists():
    #                     serializer = DoctorSlotSerializer(slots, many=True)
    #                     return Response(serializer.data, status=status.HTTP_200_OK)
    #                 else:
    #                     return Response({"message": "No available slots for this date"}, status=status.HTTP_400_BAD_REQUEST)
    #             else:
    #                 slots = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, is_booked=False, is_blocked=False)
    #                 if slots.exists():
    #                     serializer = DoctorSlotSerializer(slots, many=True)
    #                     return Response(serializer.data, status=status.HTTP_200_OK)
    #                 else:
    #                     return Response({"message": "No available slots"}, status=status.HTTP_400_BAD_REQUEST)
    #         except Appointmentslots.DoesNotExist:
    #             return Response({"error": "Slot not found"}, status=status.HTTP_400_BAD_REQUEST)
    #         except ValueError:
    #             return Response({"error": "Invalid date format. Please provide slot_date in 'YYYY-MM-DD' format"}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        
class SearchBookedAppointments(APIView):
    def get(self, request):
        try:
            doctor_id = request.query_params.get("doctor_id", None)
            query = request.query_params.get("query", None)
           
            if not doctor_id:
                return Response({"error": "Doctor ID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
           
            appointments = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, is_booked=True)
           
            if not appointments.exists():
                return Response({"error": "No appointments found for the given doctor_id."}, status=status.HTTP_404_NOT_FOUND)
           
            if query:
                filter_by_patient_name = Q(booked_by__name__icontains=query)
                filter_by_appointment_date = Q(appointment_date__icontains=query)
                filter_by_doctor_name = Q(doctor__name__icontains=query)
                filter_by_mobile_number = Q(booked_by__patient__mobile_number__icontains=query)
               
                filtered_appointments = appointments.filter(
                    filter_by_patient_name | filter_by_doctor_name | filter_by_mobile_number | filter_by_appointment_date
                )
               
                if not filtered_appointments.exists():
                    return Response({"error": "No appointments found."}, status=status.HTTP_404_NOT_FOUND)
               
                appointments = filtered_appointments
            else:
                appointments = appointments
           
            serializer = BookedAppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
       
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class TodaysSlot(APIView):
    def get(self, request):
        try:
            doctor_id = request.query_params.get('doctor_id')
            if not doctor_id:
                return Response({"error": "doctor_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
            current_date = date.today()
            appointments = Appointmentslots.objects.filter(
                doctor__doctor_id=doctor_id,
                appointment_date=current_date,
            )
            serializer = DoctorSlotSerializer(appointments, many=True)
            if not serializer.data:
                    return Response({"error": "No slots found for the current date"}, status=status.HTTP_404_NOT_FOUND)
            return Response(serializer.data)
 
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
class CountBookedAppointments(APIView):
    def get(self, request):
        try:
            doctor_id = request.query_params.get("doctor_id", None)
            if not doctor_id:
                return Response({"error": "Doctor ID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
           
            booked_appointments_count = Appointmentslots.objects.filter(doctor__doctor_id=doctor_id, is_booked=True).count()
           
            return Response({"doctor_id": doctor_id, "booked_appointments_count": booked_appointments_count}, status=status.HTTP_200_OK)
       
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class TotalAppointmentsCount(APIView):
 
    # def get(self, request):
    #     doctor_id = request.query_params.get("doctor_id")
    #     dates_str = request.query_params.getlist("dates")

    #     if not doctor_id or not dates_str:
    #         return Response({"error": "Doctor ID and dates are required."}, status=status.HTTP_400_BAD_REQUEST)

    #     results = []

    #     for date_str in dates_str:
    #         try:
    #             date = datetime.strptime(date_str, '%Y-%m-%d').date()
    #             count = Appointmentslots.objects.filter(
    #                 doctor__doctor_id=doctor_id,
    #                 appointment_date=date
    #             ).count()
    #             results.append({"date": date_str, "count": count})
    #         except ValueError:
    #             return Response({"error": f"Incorrect date format for {date_str}. Please provide date in YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)

    #     return Response(results, status=status.HTTP_200_OK)
    def get(self, request):
        doctor_ids = request.query_params.getlist("doctor_id") 
        dates_str = request.query_params.getlist("dates")

        if not doctor_ids or not dates_str:
            return Response({"error": "Doctor IDs and dates are required."}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        for doctor_id in doctor_ids:  
            doctor_results = {"doctor_id": doctor_id, "slots": []}
            for date_str in dates_str:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    count = Appointmentslots.objects.filter(
                        doctor__doctor_id=doctor_id,
                        appointment_date=date
                    ).count()
                    doctor_results["slots"].append({"date": date_str, "count": count})
                except ValueError:
                    return Response({"error": f"Incorrect date format for {date_str}. Please provide date in YYYY-MM-DD format."}, status=status.HTTP_400_BAD_REQUEST)
            results.append(doctor_results)

        return Response(results, status=status.HTTP_200_OK)
    
class CompletedAppointment(APIView):
    def patch(self, request):
        appointment_id = request.data.get('appointment_id')
        if not appointment_id:
            return Response({"error": "Appointment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            appointment = Appointmentslots.objects.get(id=appointment_id)
        except Appointmentslots.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
       
        appointment.is_complete = True
        appointment.save()
 
        return Response({"success": "Appointment is completed"}, status=status.HTTP_200_OK)
    
class CanceledAppointment(APIView):
    def patch(self, request):
        appointment_id = request.data.get('appointment_id')
        if not appointment_id:
            return Response({"error": "Appointment ID is required"}, status=status.HTTP_400_BAD_REQUEST)
 
        try:
            appointment = Appointmentslots.objects.get(id=appointment_id)
        except Appointmentslots.DoesNotExist:
            return Response({"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND)
       
        appointment.is_canceled = True
        appointment.save()
 
        return Response({"success": "Appointment is canceled"}, status=status.HTTP_200_OK)
    
    
    
    
    
    
    
    
    
    
    
class CreateMeetLinkView(APIView):
    def post(self, request):
        doctor_email = request.data.get("doctor_email")
        patient_email = request.data.get("patient_email")
        meeting_topic = request.data.get("meeting_topic", "Meeting")
        
        # Validate email fields
        if not doctor_email or not patient_email:
            return Response({"error": "Both 'doctor_email' and 'patient_email' fields are required."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        meet_link = "https://meet.google.com/new"  # Same link for both

        # Send the same meeting link to both emails
        self.send_meeting_link(doctor_email, meet_link, meeting_topic)
        self.send_meeting_link(patient_email, meet_link, meeting_topic)

        return Response({"message": "Meeting links sent successfully."}, status=status.HTTP_200_OK)

    def send_meeting_link(self, recipient_email, meeting_link, meeting_topic):
        subject = "Your Meeting Link"
        message = (
            f"Hello,\n\n"
            f"You have been invited to a meeting on the topic: {meeting_topic}.\n\n"
            f"Please join using the following link:\n{meeting_link}\n\n"
            f"Best regards,\nYour Team"
        )
        # Send the email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email], fail_silently=False)