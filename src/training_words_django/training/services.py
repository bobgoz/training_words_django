"""Сервисная логика для приложения Training."""

import uuid

from django.template.defaultfilters import slugify
from eng_to_ru import Translator
from unidecode import unidecode


def clean_session(request):
    """Очистка сессии."""
    request.session.pop('training_words', None)
    request.session.pop('training_current_index', None)
    request.session.pop('training_settings', None)
    request.session.pop('training_session_id', None)
    request.session.pop('training_correct_count', None)
    request.session.pop('training_incorrect_count', None)
    request.session.pop('training_total_words', None)


def image_unique_name(instance, filename):
    """Задание уникального имени для картинки."""
    ext = filename.split('.')[-1]
    return f'images/{instance.user.id}/{uuid.uuid4().hex}.{ext}'


def translator(word) -> str:
    """Перевод английского слова в русское."""
    translator = Translator()
    return translator.run(word)


def generate_slug(word):
    """Гененация slug."""
    from .models import Word

    base_slug = slugify(unidecode(word))

    if not base_slug:
        base_slug = 'word'

    slug = base_slug
    n = 1

    while Word.objects.filter(slug=slug).exists():
        slug = f'{base_slug}_{n}'
        n += 1

    return slug
