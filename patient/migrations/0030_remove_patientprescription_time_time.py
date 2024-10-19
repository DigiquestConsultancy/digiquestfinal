# Generated by Django 5.0.4 on 2024-09-05 10:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0029_patientrecord_height_patientrecord_weight'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patientprescription',
            name='time',
        ),
        migrations.CreateModel(
            name='Time',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('evening', 'Evening'), ('night', 'Night')], max_length=50)),
                ('is_selected', models.BooleanField(default=False)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patientvarrydetails')),
            ],
        ),
    ]
