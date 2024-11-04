from django.db import models
from django.db import models

# Create your models here.
from django.db import models

class ReceptionRegister(models.Model):
    mobile_number=models.CharField(max_length=15)
    is_doctor=models.BooleanField(default=False, null=True, blank=True)
    doctor=models.ForeignKey("doctor.DoctorRegister", on_delete=models.CASCADE)
    password=models.CharField(max_length=225, null=True, blank=True)
    is_reset=models.BooleanField(default=False, null=True, blank=True)
    
    def __str__(self):
        return f"ReceptionRegister ID: {self.pk}"


def  save_doctor_pic(instance,filename):
    return f'static/{instance.name}/{filename}'
def  save_doctor_doc(instance,filename):
    return f'static/{instance.name}/{filename}'



class ReceptionDetails(models.Model):
    reception =models.ForeignKey(ReceptionRegister, on_delete=models.CASCADE)
    
    name= models.CharField(max_length=100)
    age= models.IntegerField(null=True, blank=True)
    address= models.TextField(null=True, blank=True)
    date_of_birth=models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=6, choices=(('male', 'Male'), ('female', 'Female'), ('others', 'Others')))
    specialization=models.CharField(max_length=150,null=True, blank=True)
    profile_pic= models.FileField(upload_to= save_doctor_pic,  null=True, blank=True)
    qualification=models.CharField(max_length=100,null=True, blank=True)   
    is_verified = models.BooleanField(default=False, null=True, blank=True) 
      
    def __str__(self):
        return self.name
