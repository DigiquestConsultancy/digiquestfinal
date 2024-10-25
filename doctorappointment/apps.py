from django.apps import AppConfig


class DoctorappointmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'doctorappointment'


    def ready(self):
        import doctorappointment.signals  # Ensure this import path matches your app structure

