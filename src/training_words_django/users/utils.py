"""Утилиты для приложения users."""

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_verification_email(*, request, user):
    """Отправляет пользователю ссылку для подтверждения почты."""

    verification_url = request.build_absolute_uri(
        reverse_lazy(
            "verify_email",
            kwargs={
                "uidb64": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            },
        )
    )
    message = render_to_string(
        "registration/verify_email.txt",
        {
            "user": user,
            "activation_url": verification_url,
        },
    )
    transaction.on_commit(
        lambda: send_mail(
            subject="Подтвердите адрес электронной почты",
            message=message,
            from_email=None,
            recipient_list=[user.email],
        )
    )
