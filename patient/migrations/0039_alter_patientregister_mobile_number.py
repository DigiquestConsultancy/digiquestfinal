# Generated by Django 4.2.16 on 2024-11-02 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0038_patientvarrydetails_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patientregister',
            name='mobile_number',
            field=models.CharField(max_length=15),
        ),
    ]
