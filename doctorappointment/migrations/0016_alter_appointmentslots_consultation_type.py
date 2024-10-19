# Generated by Django 4.2.16 on 2024-10-03 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctorappointment', '0015_appointmentslots_consultation_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointmentslots',
            name='consultation_type',
            field=models.CharField(choices=[('walk-in', 'Walk-In'), ('online', 'Online')], default='walk-in', max_length=20),
        ),
    ]
