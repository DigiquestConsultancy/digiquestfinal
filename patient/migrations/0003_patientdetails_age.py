# Generated by Django 5.0.4 on 2024-06-19 11:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0002_delete_bookslot'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientdetails',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
