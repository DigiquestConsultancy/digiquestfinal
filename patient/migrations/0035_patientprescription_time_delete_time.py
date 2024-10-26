# Generated by Django 4.2.16 on 2024-10-19 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0034_patientdetails_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='patientprescription',
            name='time',
            field=models.CharField(choices=[('morning', 'Morning'), ('morning-afternoon', 'Morning-Afternoon'), ('morning-evening', 'Morning-Evening'), ('morning-afternoon-evening', 'Morning-Afternoon-Evening'), ('morning-afternoon-evening-night', 'Morning-Afternoon-Evening-Night'), ('afternoon', 'Afternoon'), ('evening', 'Evening'), ('night', 'Night')], default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Time',
        ),
    ]
