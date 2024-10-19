# Generated by Django 4.2.16 on 2024-10-01 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctorappointment', '0010_appointmentslots_is_online'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointmentslots',
            name='is_online',
        ),
        migrations.AlterField(
            model_name='appointmentslots',
            name='appointment_type',
            field=models.CharField(choices=[('walk-in', 'Walk-In'), ('online', 'Online')], default='online', max_length=20),
        ),
    ]
