"""Модуль с сигналами для приложения training."""

import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver
from dropbox.exceptions import ApiError

from .models import Word

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Word)
def delete_old_image_on_update(sender, instance, **kwargs):
    """Сигнал для удаления старой картинки при обновлении экземпляра модели."""
    if not instance.pk:
        return
    # Получение старого объекта из БД.
    old_image = sender.objects.get(pk=instance.pk).image
    new_image = instance.image

    if old_image and old_image.name != new_image.name:
        try:
            old_image.delete(save=False)
            logging.debug(
                'Удалёна картинка в сигнале слова %s: %s',
                instance.pk,
                old_image.name,
            )
        except ApiError as e:
            logging.debug(
                f'Неудачное удаление картинки через image.delete(): {e}'
                'Произошла очистка поля image в базе данных.',
                instance.pk,
                old_image.name,
            )
            instance.image = None
