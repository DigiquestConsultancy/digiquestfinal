# Generated by Django 4.2.16 on 2024-11-02 11:56

from django.db import migrations, models
import doctor.models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0037_alter_doctorregister_mobile_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalsdetails',
            name='doc_file',
            field=models.FileField(blank=True, null=True, upload_to=doctor.models.save_doc),
        ),
    ]