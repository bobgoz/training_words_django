from django.conf import settings
from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

BIO_FIELD_MAX_LENGTH = 500


class Profile(models.Model):
    """Профиль пользователя"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='profile',
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(
        'О себе',
        max_length=BIO_FIELD_MAX_LENGTH,
        blank=True,
    )

    class Meta:
        verbose_name = 'профиль'
        verbose_name_plural = 'профили'

    def __str__(self):
        return f'Профиль {self.user.username}'
