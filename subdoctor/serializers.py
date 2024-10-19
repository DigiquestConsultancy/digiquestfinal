from rest_framework import serializers

from subdoctor.models import SubdoctorDetail, SubdoctorRegister

class SubdoctorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model= SubdoctorRegister
        fields= "__all__"
        
class SubdoctorDetialsSerializers(serializers.ModelSerializer):
    class Meta:
        model= SubdoctorDetail
        fields="__all__"
