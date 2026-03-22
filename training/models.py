from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

WORD_FIELD_MAX_LENGTH = 150

DEFINITION_FIELD_MAX_LENGTH = 200


class Word(models.Model):
    """Класс слова"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    word = models.CharField(
        'Слово',
        max_length=WORD_FIELD_MAX_LENGTH,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField('Активное слово', default=False)
    definition = models.CharField(
        'Определение слова',
        max_length=DEFINITION_FIELD_MAX_LENGTH,
        help_text='Опциональное поле. Определение слова.'
        f' Количество символов не более {DEFINITION_FIELD_MAX_LENGTH}',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'слово'
        verbose_name_plural = 'слова'
        ordering = ('-created_at',)
