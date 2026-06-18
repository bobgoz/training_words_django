from django.db.models.signals import post_save
from django.dispatch import receiver

from training.models import Word
from training.tasks import upload_image_to_dropbox


@receiver(post_save, sender=Word)
def handle_word_image(sender, instance, created, **kwargs):
    if instance.image:
        upload_image_to_dropbox.delay(instance.id)
