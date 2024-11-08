# Generated by Django 5.0.4 on 2024-08-13 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctorappointment', '0007_appointmentslots_is_canceled'),
        ('patient', '0017_rename_appointment_id_patientdocumentbyappointmentid_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientdocumentbyappointmentid',
            name='appointment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctorappointment.appointmentslots'),
        ),
        migrations.AlterField(
            model_name='patientdocumentbyappointmentid',
            name='document_type',
            field=models.CharField(choices=[('report', 'Report'), ('prescription', 'Prescription'), ('invoice', 'Invoice')], max_length=50),
        ),
    ]
