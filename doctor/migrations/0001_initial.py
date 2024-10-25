# Generated by Django 5.0.6 on 2024-06-14 07:36

import doctor.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Appointmentslot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateField()),
                ('appointment_slot', models.TimeField()),
                ('is_booked', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=250)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('others', 'Others')], max_length=6)),
                ('registration_no', models.IntegerField()),
                ('doc_file', models.FileField(blank=True, null=True, upload_to=doctor.models.save_doctor_doc)),
                ('specialization', models.CharField(max_length=150)),
                ('experience', models.IntegerField()),
                ('profile_pic', models.FileField(blank=True, null=True, upload_to=doctor.models.save_doctor_pic)),
                ('qualification', models.CharField(max_length=100)),
                ('is_verified', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.CharField(choices=[('best', 'Best'), ('good', 'Good'), ('average', 'Average'), ('bad', 'Bad'), ('worst', 'Worst')], max_length=10)),
                ('comment', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DoctorRegister',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_number', models.IntegerField()),
                ('is_doctor', models.BooleanField(blank=True, default=True, null=True)),
            ],
        ),
    ]