from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from .models import Profile

@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    """ Создание профиля при создании (регистрации) пользователя """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """ Сохранение профиля при редактировании модели пользователя"""
    instance.profile.save()

post_save.connect(create_user_profile, sender=get_user_model())

