from rest_framework import serializers

from doctorappointment.models import Appointmentslots

class BookedAppointmentSerializer(serializers.ModelSerializer):
    booked_by = serializers.CharField(source='booked_by.name', read_only=True)
    patient_id= serializers.IntegerField(source='booked_by.id', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    appointment_id = serializers.IntegerField(source='id')
    mobile_number= serializers.IntegerField(source='booked_by.patient.mobile_number', read_only=True)
    patient_id = serializers.IntegerField(source='booked_by.patient.id', read_only=True)
    appointment_date = serializers.DateField() 

    class Meta:
        model = Appointmentslots
       
        fields = ['appointment_date', 'appointment_slot', 'booked_by','appointment_id','doctor_name','mobile_number','patient_id','is_blocked','is_patient','is_canceled','is_complete','is_booked','appointment_type','is_appointment','patient_id']


class DoctorSlotSerializer(serializers.ModelSerializer):
    booked_by = serializers.CharField(source='booked_by.name', read_only=True)
    class Meta:
        model = Appointmentslots
        fields = ['id', 'appointment_date', 'appointment_slot', 'is_booked', 'booked_by','is_blocked','is_patient','is_canceled','consultation_type']
        
class AppointmentslotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointmentslots
        fields = '__all__'