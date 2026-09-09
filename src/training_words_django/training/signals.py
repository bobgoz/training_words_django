"""Модуль с сигналами для приложения training."""

import logging

from django.core.files.storage import default_storage
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Word

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Word)
def delete_old_image_on_update(sender, instance, **kwargs):
    """Сигнал для удаления старой картинки при обновлении экземпляра модели."""
    if not instance.pk:
        return
    # Получение старого объекта из БД.6666
    old_image = sender.objects.get(pk=instance.pk).image
    if old_image:
        if default_storage.exists(old_image.name):
            old_image.delete()
            logging.debug("Картинка удалилась из хранилища через сигнал.")
