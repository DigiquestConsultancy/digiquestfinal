import hashlib
from django.db import models
from django.conf import settings
 
 
def hash_value(value):
    """Hash a value with SHA256."""
    return hashlib.sha256(value.encode()).hexdigest()
 
 
class DigiAdminLogin(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=64)
 
    def save(self, *args, **kwargs):
        if self.pk is None:  
            self.username = hash_value(self.username)
            self.password = hash_value(self.password)
        super().save(*args, **kwargs)
 
    @staticmethod
    def check_credentials(username, password):
        """Check if the hashed username and password match."""
        hashed_username = hash_value(username)
        hashed_password = hash_value(password)
        try:
            return DigiAdminLogin.objects.get(
                username=hashed_username, password=hashed_password)
        except DigiAdminLogin.DoesNotExist:
            return None