import os
from django.db import models

from doctorappointment.models import Appointmentslots

class PatientRegister(models.Model):
    mobile_number=models.IntegerField()
    password=models.CharField(max_length=225)

def save_document(instance,filename):
    return f'static/document'

def get_prescription_upload_path(instance, filename):
    base_directory = 'static'
    patient_details = PatientVarryDetails.objects.get(appointment_id=instance.appointment)
    patient_name = patient_details.name
    patient_folder = f"{patient_name}"
    prescription_folder = "prescriptions"
    original_filename = filename 
    file_path = os.path.join(base_directory, patient_folder, prescription_folder, original_filename)

    return file_path

def document_by_id(instance, filename):
    base_directory = 'static'
    patient_details = PatientVarryDetails.objects.get(appointment_id=instance.appointment)
    patient_name = patient_details.name
    patient_folder = f"{patient_name}"
    prescription_folder = "document"
    original_filename = filename 
    file_path = os.path.join(base_directory, patient_folder, prescription_folder, original_filename)

    return file_path




def  save_user_pic(instance,filename):
    return f'static/{instance.name}/{filename}'

def patient_report(instance,filename):
    patient = PatientDetails.objects.get(patient__mobile_number=instance.patient.patient.mobile_number)
    patient_name = patient.name
    return f'static/{patient_name}/report/{filename}'

class PatientDetails(models.Model):
    patient =models.ForeignKey(PatientRegister, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, null=True, blank=True)
    date_of_birth = models.DateField()
    age=models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=6, choices=(('male', 'Male'), ('female', 'Female'), ('others', 'Others')))
    blood_group = models.CharField(max_length=5)
    
    profile_pic= models.FileField(upload_to=save_user_pic, null=True, blank=True)
    

    def __str__(self):
        return self.name
    
    
class PatientDocument(models.Model):
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE)
    document_name=models.CharField(max_length=100)
    document_file=models.FileField(upload_to=patient_report, null=True, blank=True )
    patient_name=models.CharField(max_length=250)
    document_date=models.DateField()

    document_type=models.CharField(max_length=50, choices=[('report','Report'),('prescription','Priscription'),('invoice','Invoice')])
    


class PatientFeedback(models.Model):
    patient= models.ForeignKey(PatientRegister, on_delete=models.CASCADE)
    rating = models.CharField(max_length=10, choices= [('best', 'Best'), ('good', 'Good'), ('average', 'Average'), ('bad', 'Bad'), ('worst', 'Worst')])
    comment = models.TextField(null=True, blank=True)
    
    

    
    
    
class PatientVarryDetails(models.Model):
    patient =models.ForeignKey(PatientRegister, on_delete=models.CASCADE)
   
    mobile_number=models.IntegerField()
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    age=models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=6, choices=(('male', 'Male'), ('female', 'Female'), ('others', 'Others')))
    blood_group = models.CharField(max_length=5)
    profile_pic= models.FileField(upload_to=save_user_pic, null=True, blank=True)
    appointment=models.ForeignKey('doctorappointment.Appointmentslots', on_delete=models.CASCADE, null=True, blank=True)
    

    def __str__(self):
        return self.name



class PatientDocumentById(models.Model):
    appointment = models.ForeignKey('doctorappointment.Appointmentslots', on_delete=models.CASCADE, null=True, blank=True)
    document_name = models.CharField(max_length=100)
    document_file = models.FileField(upload_to=document_by_id, null=True, blank=True)
    patient_name = models.CharField(max_length=250)
    document_date = models.DateField()
    uploaded_by=models.CharField(max_length=50)
    document_type = models.CharField(max_length=50, choices=[('report', 'Report'), ('prescription', 'Prescription'), ('invoice', 'Invoice')])




class Time(models.Model):
    time = models.CharField(max_length=50, choices=[('morning', 'Morning'),
                                                    ('afternoon', 'Afternoon'),
                                                    ('evening', 'Evening'),
                                                    ('night', 'Night')])
    is_selected = models.BooleanField(default=False)
    appointment = models.ForeignKey('doctorappointment.Appointmentslots', on_delete=models.CASCADE)
    

    
    
class PatientPrescription(models.Model):
    patient = models.ForeignKey(PatientVarryDetails, on_delete=models.CASCADE)
    medicine_name = models.CharField(max_length=100)
    comment = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    appointment = models.ForeignKey('doctorappointment.Appointmentslots', on_delete=models.CASCADE)
    
    
class PatientRecord(models.Model):
    patient = models.ForeignKey(PatientVarryDetails, on_delete=models.CASCADE)
    blood_pressure = models.FloatField(null=True, blank=True)
    body_temperature = models.FloatField(null=True, blank=True)
    sugar_level = models.FloatField(null=True, blank=True)
    pulse_rate = models.FloatField(null=True, blank=True)
    heart_rate = models.FloatField(null=True, blank=True)
    oxygen_level = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    record_date=models.DateField()
    appointment = models.ForeignKey('doctorappointment.Appointmentslots', on_delete=models.CASCADE, null=True, blank=True)
    
    
class PatientPrescriptionFile(models.Model):
    appointment = models.ForeignKey('doctorappointment.Appointmentslots', on_delete=models.CASCADE, null=True, blank=True)
    document_file=models.FileField(upload_to=get_prescription_upload_path)
    document_date=models.DateField()
    