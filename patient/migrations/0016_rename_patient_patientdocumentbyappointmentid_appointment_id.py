# Generated by Django 5.0.4 on 2024-08-13 10:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0015_patientdocumentbyappointmentid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patientdocumentbyappointmentid',
            old_name='patient',
            new_name='appointment_id',
        ),
    ]
