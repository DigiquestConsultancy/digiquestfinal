# Generated by Django 4.2.16 on 2024-10-03 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0033_patientregister_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientdetails',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
