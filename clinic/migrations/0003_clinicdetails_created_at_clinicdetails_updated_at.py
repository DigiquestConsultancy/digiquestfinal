# Generated by Django 5.0.4 on 2024-07-02 08:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicdetails',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='clinicdetails',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]