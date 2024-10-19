from django.db import models

class SubdoctorRegister(models.Model):
    mobile_number=models.IntegerField()
    is_doctor=models.BooleanField(default=False, null=True, blank=True)
    doctor=models.ForeignKey("doctor.DoctorRegister", on_delete=models.CASCADE)



def  save_doctor_pic(instance,filename):
    return f'static/{instance.name}/{filename}'
def  save_doctor_doc(instance,filename):
    return f'static/{instance.name}/{filename}'



class SubdoctorDetail(models.Model):
    subdoctor =models.ForeignKey(SubdoctorRegister, on_delete=models.CASCADE)
    
    name= models.CharField(max_length=100)
    address= models.CharField(max_length=250,null=True, blank=True)
    date_of_birth=models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=6, choices=(('male', 'Male'), ('female', 'Female'), ('others', 'Others')))
    # registration_no= models.IntegerField(null=True, blank=True)
    # doc_file= models.FileField(upload_to= save_doctor_doc, null=True, blank=True)
    specialization=models.CharField(max_length=150)
    # experience=models.IntegerField()
    profile_pic= models.FileField(upload_to= save_doctor_pic,  null=True, blank=True)
    qualification=models.CharField(max_length=100,null=True, blank=True)   
    is_verified = models.BooleanField(default=False, null=True, blank=True) 
      
    def __str__(self):
        return self.name
