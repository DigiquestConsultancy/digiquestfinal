# Generated by Django 5.0.4 on 2024-06-18 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctordetail',
            name='registration_no',
            field=models.CharField(max_length=150),
        ),
    ]
