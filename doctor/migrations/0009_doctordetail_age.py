# Generated by Django 5.0.4 on 2024-07-19 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doctor', '0008_doctordetail_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctordetail',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
