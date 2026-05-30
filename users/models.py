from django.db import models

from django.contrib.auth.models import AbstractUser

BIO_FIELD_MAX_LENGTH = 500


class User(AbstractUser):
    """Расширенная модель пользователя"""

    bio = models.TextField('О себе', max_length=500, blank=True, null=True)
    avatar = models.ImageField(
        'Аватар', upload_to='avatars/', blank=True, null=True
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username
