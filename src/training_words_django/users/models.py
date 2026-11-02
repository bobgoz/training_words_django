from django.contrib.auth.models import AbstractUser
from django.db import models

BIO_FIELD_MAX_LENGTH = 500


class User(AbstractUser):
    """Расширенная модель пользователя"""

    bio = models.TextField("О себе", max_length=500, blank=True, null=True)
    avatar = models.ImageField(
        "Аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
    )
    email_verifed = models.BooleanField(
        "Почта подтверждена",
        default=False,
    )
    email = models.EmailField(
        "Электронная почта",
        unique=True,
        help_text="Введите свой актуальный адрес электронной почты",
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.username
