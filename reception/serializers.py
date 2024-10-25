from rest_framework import serializers


from doctorappointment.models import Appointmentslots
from reception.models import ReceptionDetails, ReceptionRegister

class ReceptionRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model= ReceptionRegister
        fields= "__all__"

class PostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=ReceptionDetails
        fields="__all__"

class ReceptionDetailsSerializer(serializers.ModelSerializer):
    mobile_number=serializers.IntegerField(source='reception.mobile_number', read_only=True)
    class Meta:
        model= ReceptionDetails
        fields=["reception_id",
        "name",
        "age",
        "address",
        "date_of_birth",
        "gender",
        "specialization",
        "profile_pic",
        "qualification",
        "is_verified",
        "mobile_number"]
        
class AllAppointmentslotsSerializer(serializers.ModelSerializer):
    booked_by = serializers.CharField(source='booked_by.name', read_only=True)
    patient_id = serializers.CharField(source='booked_by.patient.id', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    appointment_id = serializers.IntegerField(source='id')
    mobile_number= serializers.IntegerField(source='booked_by.patient.mobile_number', read_only=True)
    appointment_date = serializers.DateField() 

    class Meta:
        model = Appointmentslots
        fields = ['id','doctor_name','booked_by','appointment_id','mobile_number','appointment_date','appointment_slot','appointment_type','is_booked','is_blocked','is_canceled','is_complete','is_patient','doctor','patient_id']
