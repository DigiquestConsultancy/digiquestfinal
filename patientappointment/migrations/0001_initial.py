# Generated by Django 5.0.4 on 2024-06-15 08:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctor', '0002_initial'),
        ('doctorappointment', '0001_initial'),
        ('patient', '0002_delete_bookslot'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_status', models.CharField(choices=[('upcoming', 'upcoming'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='upcoming', max_length=10)),
                ('appointment_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctorappointment.appointmentslots')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctor.doctordetail')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patientdetails')),
            ],
        ),
    ]
