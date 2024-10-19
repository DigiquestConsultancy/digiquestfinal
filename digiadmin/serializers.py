from rest_framework import serializers

from doctor.models import DoctorDetail, DoctorRegister, PersonalsDetails


        
class DocDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorRegister
        fields = ['id', 'mobile_number', 'is_doctor', 'is_verified', 'is_active']

class DocDetailforSerializer(serializers.ModelSerializer):
    # Directly include fields from the related DoctorRegister model
    mobile_number = serializers.ReadOnlyField(source='doctor.mobile_number')
    is_doctor = serializers.ReadOnlyField(source='doctor.is_doctor')


    class Meta:
        model = PersonalsDetails
        fields = ['doctor', 'name', 'mobile_number', 'is_doctor', 'is_verified', 'is_active','registration_no']
        
class DoctorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorRegister
        fields = '__all__'  # or specify the fields you need

        
class DoctorDetailAdmin(serializers.ModelSerializer):
    mobile_number=serializers.IntegerField(source="doctor.mobile_number")
    class Meta:
        model = PersonalsDetails
        fields =   [
            "id",
            'name',
            'date_of_birth',
            'gender',
            'registration_no',
            'doc_file',
            'specialization',
            'experience',
            'profile_pic',
            'is_verified',
            'mobile_number',
            'is_active'
        ]
