# Generated by Django 5.0.4 on 2024-09-04 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0027_alter_patientdocumentbyid_document_file'),
    ]

    operations = [
        migrations.RenameField(
            model_name='patientrecord',
            old_name='hemoglobin',
            new_name='sugar_level',
        ),
    ]
