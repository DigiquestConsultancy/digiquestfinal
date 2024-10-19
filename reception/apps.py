# reception/apps.py

from django.apps import AppConfig

class ReceptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Adjust based on your needs
    name = 'reception'  # Replace with your app's name

    def ready(self):
        # Import the signals module to ensure signals are registered
        import reception.signals  # Adjust the import based on your app's structure
