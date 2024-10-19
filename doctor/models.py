import datetime
from django.db import models


class DoctorRegister(models.Model):
    mobile_number=models.IntegerField()
    is_doctor=models.BooleanField(default=True, null=True, blank=True)
    password=models.CharField(max_length=225)
    is_verified = models.BooleanField(default=False, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    is_created = models.DateTimeField(auto_now_add=True)
    is_updated = models.DateTimeField(auto_now=True)
    


    def __str__(self):
        return str(self.mobile_number)

    # Override save method to sync with PersonalsDetails
    def save(self, *args, **kwargs):
        # If is_verified is True, update the related PersonalsDetails
        if self.is_verified:
            details = self.details.first()  # Assuming one-to-one relationship
            if details and not details.is_verified:
                details.is_verified = True
                details.save(update_fields=['is_verified'])
        super(DoctorRegister, self).save(*args, **kwargs)    
    

    
def  save_doctor_pic(instance,filename):
    return f'static/{instance.name}/{filename}'
def  save_doctor_doc(instance,filename):
    return f'static/{instance.name}/{filename}'

class Qualification(models.Model):
    QUALIFICATION_CHOICES = [
        ('MBBS', 'MBBS'),
        ('MD', 'MD'),
        ('PhD', 'PhD'),
        ('Diploma', 'Diploma'),
        ('Fellowship', 'Fellowship'),
    ] 
    qualification = models.CharField(max_length=50, choices=QUALIFICATION_CHOICES)
    is_selected = models.BooleanField(default=False)
    doctor = models.ForeignKey(
        DoctorRegister, 
        on_delete=models.CASCADE, 
        related_name='qualifications'
    )


class DoctorDetail(models.Model):
    doctor =models.ForeignKey(DoctorRegister, on_delete=models.CASCADE, related_name='detail')
    
    name= models.CharField(max_length=100)
    address= models.CharField(max_length=250)
    date_of_birth=models.DateField()
    gender = models.CharField(max_length=6, choices=(('male', 'Male'), ('female', 'Female'), ('others', 'Others')))
    registration_no= models.CharField(max_length=150)
    doc_file= models.FileField(upload_to= save_doctor_doc, null=True, blank=True)
    specialization=models.CharField(max_length=150)
    experience=models.IntegerField()
    profile_pic= models.FileField(upload_to= save_doctor_pic,  null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True, blank=True) 
    is_active= models.BooleanField(default=False)
    age=models.IntegerField(null=True, blank=True)
    hospital_name=models.CharField(max_length=250, null=True, blank=True)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(PersonalsDetails, self).save(*args, **kwargs)
        self.update_doctor_verification_status()

    def update_doctor_verification_status(self):
        any_verified = PersonalsDetails.objects.filter(doctor=self.doctor, is_verified=True).exists()
        self.doctor.is_verified = any_verified
        any_active = PersonalsDetails.objects.filter(doctor=self.doctor, is_active=True).exists()
        self.doctor.is_active = any_active
        self.doctor.save()


class DoctorFeedback(models.Model):
    doctor= models.ForeignKey(DoctorRegister, on_delete=models.CASCADE)
    rating = models.CharField(max_length=10, choices= [('best', 'Best'), ('good', 'Good'), ('average', 'Average'), ('bad', 'Bad'), ('worst', 'Worst')])
    comment = models.TextField(null=True, blank=True)   
    
    
class Symptoms(models.Model):
    symptoms_name = models.CharField(max_length=100)
 
    def __str__(self):
        return self.symptoms_name
 
 
class SymptomsDetail(models.Model):
    symptoms = models.ForeignKey(Symptoms, on_delete=models.CASCADE)
    since = models.TextField(null=True, blank=True)
    severity = models.CharField(max_length=10, choices=[('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe')])
    more_options =  models.TextField(null=True, blank=True)
    appointment = models.ForeignKey('doctorappointment.Appointmentslots', on_delete=models.CASCADE)
    symptom_date = models.DateField()
  
class OpdDays(models.Model):
    doctor= models.ForeignKey(DoctorRegister, on_delete=models.CASCADE)
    start_day = models.TextField()
    end_day = models.TextField()
    start_time= models.TimeField()
    end_time = models.TimeField()
    
    
def doctor_pic(instance, filename):
    return f'static/{instance.name}/{filename}'   

def  save_doc(instance,filename):
    return f'static/{instance.name}/{filename}'
    
class PersonalsDetails(models.Model):
    doctor = models.ForeignKey(DoctorRegister, on_delete=models.CASCADE, related_name='details')
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=6, choices=(
        ('male', 'Male'), ('female', 'Female'), ('others', 'Others')))
    registration_no = models.CharField(max_length=150)
    specialization = models.CharField(max_length=150)
    experience = models.IntegerField()
    profile_pic = models.FileField(
        upload_to=doctor_pic, null=True, blank=True)
    doc_file= models.FileField(upload_to= save_doc, null=True, blank=True)
    email = models.EmailField(
        max_length=254, null=True, blank=True)
    languages_spoken = models.CharField(max_length=255, null=True, blank=True)
    is_update = models.BooleanField(default=False, null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True, blank=True) 
    is_active= models.BooleanField(default=False)
 
    def __str__(self):
        return str(self.doctor.mobile_number)


    def save(self, *args, **kwargs):
        if self.is_verified:
            if not self.doctor.is_verified:
                self.doctor.is_verified = True
                self.doctor.save(update_fields=['is_verified'])
        else:
            if self.doctor.is_verified:
                self.doctor.is_verified = False
                self.doctor.save(update_fields=['is_verified'])

        
        if self.is_active:
            if not self.doctor.is_active:
                self.doctor.is_active = True
                self.doctor.save(update_fields=['is_active'])
        else:
            if self.doctor.is_active:
                self.doctor.is_active = False
                self.doctor.save(update_fields=['is_active'])

        super(PersonalsDetails, self).save(*args, **kwargs)





 
class Address(models.Model):
    doctor = models.ForeignKey(DoctorRegister, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    street_address = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=20, null=True, blank=True)
    landmark = models.CharField(
        max_length=255, null=True, blank=True)
    is_update = models.BooleanField(default=False, null=True, blank=True)
 
    def __str__(self):
        return f'{self.street_address}, {self.city}, {self.state}, {self.country}'
 
 
def save_doc(instance, filename):
    return f'static/{instance.clinic_name}/{filename}'
 
 
class Opd(models.Model):
    doctor = models.ForeignKey(DoctorRegister, on_delete=models.CASCADE)
    clinic_name = models.CharField(max_length=100, null=True, blank=True)
    doc_file = models.FileField(upload_to=save_doc, null=True, blank=True)
    start_day = models.TextField(null=True, blank=True)
    end_day = models.TextField(null=True, blank=True)
    is_update = models.BooleanField(default=False, null=True, blank=True)
 
 
class OpdTime(models.Model):
    time = models.ForeignKey(Opd, on_delete=models.CASCADE)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
 