# Generated by Django 4.2.16 on 2024-11-04 11:02

from django.db import migrations, models
import doctor.models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0039_alter_personalsdetails_doc_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalsdetails',
            name='doc_file',
            field=models.FileField(blank=True, null=True, upload_to=doctor.models.save_doc),
        ),
    ]
