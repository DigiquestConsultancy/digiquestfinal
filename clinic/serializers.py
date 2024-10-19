from rest_framework import serializers

from clinic.models import ClinicDetails, ClinicRegister
from patient.models import PatientDetails, PatientVarryDetails
from doctor.models import DoctorDetail, DoctorRegister

class ClinicRegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model= ClinicRegister
        fields= ["mobile_number",
        "doctor",
        "is_doctor"]
        
class ClinicDetailsSerializers(serializers.ModelSerializer):
    
    mobile_number=serializers.IntegerField(source='clinic.mobile_number', read_only=True)
    class Meta:
        model= ClinicDetails
        fields=["clinic_id",
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
        
class ClinicDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model=ClinicDetails
        fields='__all__'

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorRegister
        fields = '__all__'
        
class DoctorDetailClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model=DoctorDetail
        fields=['doctor_id','name']
        
class PatientDetailForSearchSerializer(serializers.ModelSerializer):
    mobile_number=serializers.IntegerField(source='patient.mobile_number', read_only=True)
    class Meta:
        model=PatientVarryDetails 
        fields=['patient','name','mobile_number','appointment']
        