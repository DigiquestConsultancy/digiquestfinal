# Generated by Django 5.0.4 on 2024-06-15 08:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctor', '0002_initial'),
        ('patient', '0002_delete_bookslot'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointmentslots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateField()),
                ('appointment_slot', models.TimeField()),
                ('is_booked', models.BooleanField(default=False)),
                ('booked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='patient.patientdetails')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctor.doctordetail')),
            ],
        ),
    ]
