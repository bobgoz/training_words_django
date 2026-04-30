from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    """Создание профиля при создании (регистрации) пользователя"""
    if created:
        print('Создано!')
        Profile.objects.create(user=instance)
