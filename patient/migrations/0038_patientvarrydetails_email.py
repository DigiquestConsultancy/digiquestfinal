# Generated by Django 4.2.16 on 2024-10-23 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0037_patientrecord_bmi'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientvarrydetails',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
