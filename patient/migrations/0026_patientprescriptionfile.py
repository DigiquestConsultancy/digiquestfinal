# Generated by Django 5.0.4 on 2024-08-24 11:17

import django.db.models.deletion
import patient.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctorappointment', '0007_appointmentslots_is_canceled'),
        ('patient', '0025_alter_patientrecord_record_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientPrescriptionFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_file', models.FileField(upload_to=patient.models.get_prescription_upload_path)),
                ('document_date', models.DateField()),
                ('appointment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='doctorappointment.appointmentslots')),
            ],
        ),
    ]