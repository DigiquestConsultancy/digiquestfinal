# Generated by Django 5.0.4 on 2024-08-12 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0013_alter_patientrecord_patient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientprescription',
            name='time',
            field=models.CharField(max_length=50),
        ),
    ]
