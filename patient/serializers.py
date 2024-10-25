from rest_framework import serializers

from doctorappointment.models import Appointmentslots
from .models import PatientDetails, PatientDocument, PatientDocumentById, PatientFeedback, PatientPrescription, PatientPrescriptionFile,  PatientRecord, PatientRegister, PatientVarryDetails

class PatientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model= PatientRegister
        fields= "__all__"

class PatientDetailSerializer(serializers.ModelSerializer):
    mobile_number = serializers.IntegerField(source='patient.mobile_number', read_only=True)

    class Meta:
        model = PatientDetails
        fields =('id','name', 'address', 'age','blood_group','date_of_birth', 'gender','profile_pic','mobile_number','email') 

class PatientDetailSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = PatientDetails
        fields ="__all__"

        
class PatientDocumentSerializermobile(serializers.ModelSerializer):
    class Meta:
        model = PatientDocument
        fields = "__all__"
   
class PatientDocumentByIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDocumentById
        fields = ['appointment', 'document_name', 'document_file', 'patient_name', 'document_date', 'document_type']

class PatientDocumentSearchSerializer(serializers.ModelSerializer):
    patient_name=serializers.CharField(source='patient.name', read_only=True)
    class Meta:
        model = PatientDocument
        fields = ['document_name','document_type','document_date','document_file','patient_name']


        
class PatientPrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model= PatientPrescription
        fields="__all__"
        
class PatientFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientFeedback
        fields = "__all__"

class MyAppointmentSerializer(serializers.ModelSerializer):
    booked_by = serializers.CharField(source='booked_by.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    doctor_mobile = serializers.IntegerField(source='doctor__doctor.mobile_number', read_only=True)

    class Meta:
        model = Appointmentslots
        fields = ['id', 'doctor_mobile' ,'appointment_date', 'appointment_slot', 'is_booked', 'booked_by', 'doctor_name', 'doctor_specialization']
        
        
class PatientRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientRecord
        fields ="__all__"
        
class PatientVarryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientVarryDetails
        fields = ['id','mobile_number', 'name', 'address', 'date_of_birth', 'age', 'gender', 'blood_group', 'profile_pic', 'appointment',"email"]
        
class PatientDocumentSerializer(serializers.ModelSerializer):
    document_file = serializers.SerializerMethodField()
    # patient = serializers.CharField(source='appointment__booked_by.name', read_only=True)

    class Meta:
        model = PatientDocumentById
        fields = [
            'id',
            'document_name',
            'document_file',
            'patient_name',
            'document_date',
            'uploaded_by',
            'document_type',
        ]

    def get_document_file(self, obj):
        return obj.document_file.url if obj.document_file else None
    
class PatientViewDocument(serializers.ModelSerializer):
    class Meta:
        model = PatientDocumentById
        fields = ['id','document_file']
        
    
class PatientPrescriptionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPrescriptionFile
        fields =  "__all__"
        
 