# Generated by Django 5.0.4 on 2024-08-13 09:22

import django.db.models.deletion
import patient.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0014_alter_patientprescription_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientDocumentByAppointmentId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.CharField(max_length=100)),
                ('document_file', models.FileField(blank=True, null=True, upload_to=patient.models.patient_report)),
                ('patient_name', models.CharField(max_length=250)),
                ('document_date', models.DateField()),
                ('document_type', models.CharField(choices=[('report', 'Report'), ('prescription', 'Priscription'), ('invoice', 'Invoice')], max_length=50)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patientvarrydetails')),
            ],
        ),
    ]
