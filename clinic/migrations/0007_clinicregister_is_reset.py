# Generated by Django 4.2.16 on 2024-09-27 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0006_alter_clinicregister_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinicregister',
            name='is_reset',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]