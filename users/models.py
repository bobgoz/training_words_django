from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

BIO_FIELD_MAX_LENGTH = 500


class Profile(models.Model):
    """Профиль пользователя"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField('О себе', max_length=BIO_FIELD_MAX_LENGTH, blank=True)
    
    def __str__(self):
        return f'Профиль {self.user.username}'
