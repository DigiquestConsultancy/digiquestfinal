# reception/apps.py

from django.apps import AppConfig

class ClinicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Adjust based on your needs
    name = 'clinic'  # Replace with your app's name

    def ready(self):
        # Import the signals module to ensure signals are registered
        import clinic.signals  # Adjust the import based on your app's structure
