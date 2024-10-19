from rest_framework import serializers

from doctorappointment.models import Appointmentslots
# from doctor.models import Appointmentslot

from .models import BookSlot

class BookSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookSlot
        fields = "__all__"

class PatientSlotSerializer(serializers.ModelSerializer):
    booked_by = serializers.CharField(source='booked_by.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    
    class Meta:
        model = Appointmentslots
        fields = ['id', 'appointment_date', 'appointment_slot', 'is_booked', 'booked_by','doctor_name','doctor_specialization']
        
        
class MyAppointmentSerializer(serializers.ModelSerializer):
    booked_by = serializers.CharField(source='booked_by.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    doctor_mobile = serializers.IntegerField(source='doctor__doctor.mobile_number', read_only=True)

    class Meta:
        model = Appointmentslots
        fields = ['id', 'doctor_mobile' ,'appointment_date', 'appointment_slot', 'is_booked', 'booked_by', 'doctor_name', 'doctor_specialization']
        
        
class AppointmentMinimalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Appointmentslots
        fields = ['id','appointment_date']