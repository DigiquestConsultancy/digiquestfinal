# Generated by Django 4.2.16 on 2024-09-30 09:15

from django.db import migrations, models
import doctor.models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0015_alter_doctordetail_doctor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='personalsdetails',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='personalsdetails',
            name='is_verified',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AlterField(
            model_name='personalsdetails',
            name='doc_file',
            field=models.FileField(blank=True, null=True, upload_to=doctor.models.save_doc),
        ),
    ]
