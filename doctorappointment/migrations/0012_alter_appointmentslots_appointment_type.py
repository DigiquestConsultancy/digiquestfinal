# Generated by Django 4.2.16 on 2024-10-01 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctorappointment', '0011_remove_appointmentslots_is_online_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointmentslots',
            name='appointment_type',
            field=models.CharField(choices=[('walk-in', 'Walk-In'), ('online', 'Online')], default='walk-in', max_length=20),
        ),
    ]
