from rest_framework import serializers


from .models import   Address, DoctorFeedback, DoctorRegister, DoctorDetail, Opd, OpdDays, OpdTime, PersonalsDetails, Qualification, Symptoms, SymptomsDetail

class DoctorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model= DoctorRegister
        fields= "__all__"



class DoctorDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDetail
        fields =   "__all__"

    
class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = "__all__"       
        
class DetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDetail
        fields = [
            "name",
            "specialization", 
            "experience",
            "address",
            "profile_pic",
            "doc_file",
            "registration_no",
        ]

class DoctorNameSpecializationSerializer(serializers.ModelSerializer):
    specializations = serializers.CharField(source="specialization")
    id = serializers.CharField(source='doctor.id', read_only=True)
    mobile_number=serializers.IntegerField(source='doctor.mobile_number')
    qualifications = QualificationSerializer(source='doctor.qualifications', many=True)
    

    class Meta:
        model = DoctorDetail
        fields =  [
            "mobile_number",
            "gender",
            "name",
            "qualifications",
            "specializations", 
            "experience",
            "address",
            "profile_pic",
            "id"
            
        ]

class DoctorFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorFeedback
        fields = "__all__"

class DoctornameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorDetail
        fields = ['name']




class SymptomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptoms
        fields = ['id', 'symptoms_name']
        
class SymptomsDetailSerializer(serializers.ModelSerializer):
    symptoms_name = serializers.CharField(
        source='symptoms.symptoms_name', read_only=True)

    class Meta:
        model = SymptomsDetail
        fields = "__all__"
        
class OpdDaysSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OpdDays
        fields = '__all__'
        
class PersonalsDetailsSerializer(serializers.ModelSerializer):
    mobile_number = serializers.IntegerField(source="doctor.mobile_number")
    class Meta:
        model = PersonalsDetails
        fields = [
            'name',
            'profile_pic',
            'mobile_number',
            'date_of_birth',
            'gender',
            'registration_no',
            'email',
            'specialization',
            'experience',
            'languages_spoken',
            'is_update',
            'doctor',
            'doc_file',
           
        ]
 
 
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
 
 
class OpdDaysSerializers(serializers.ModelSerializer):
    class Meta:
        model = Opd
        fields = '__all__'

class OpdTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpdTime
        fields = '__all__'
        
        
class SearchDetailsSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)
    mobile_number = serializers.IntegerField(source="doctor.mobile_number")
    qualifications = QualificationSerializer(
        source='doctor.qualifications', many=True)
 
    class Meta:
        model = PersonalsDetails
        fields = [
            'doctor', 'name', 'date_of_birth', 'gender', 'registration_no',
            'specialization', 'experience', 'profile_pic', 'email',
            'languages_spoken', 'address',"mobile_number",'doctor','qualifications',
        ]