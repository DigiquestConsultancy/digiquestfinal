# Generated by Django 4.2.16 on 2024-09-27 12:35

from django.db import migrations, models
import django.db.models.deletion
import doctor.models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0012_personalsdetails_doc_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='opd',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='opd',
            name='start_time',
        ),
        migrations.AlterField(
            model_name='personalsdetails',
            name='doc_file',
            field=models.FileField(blank=True, null=True, upload_to=doctor.models.save_doc),
        ),
        migrations.CreateModel(
            name='OpdTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('time', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctor.opd')),
            ],
        ),
    ]
