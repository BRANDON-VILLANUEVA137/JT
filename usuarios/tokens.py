from django.db import models
from django.contrib.auth import get_user_model
from django.utils.crypto import constant_time_compare
import secrets

from usuarios.models import Usuario
User = Usuario

class EmailChangeToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    new_email = models.EmailField()
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Token for {self.user} to {self.new_email}"
    
    def is_valid(self):
        from django.utils import timezone
        return (timezone.now() - self.created_at).seconds < 3600  # 1 hour
    
    @classmethod
    def generate_token(cls, user, new_email):
        token = secrets.token_urlsafe(32)
        cls.objects.update_or_create(
            user=user,
            defaults={'new_email': new_email, 'token': token}
        )
        return token
