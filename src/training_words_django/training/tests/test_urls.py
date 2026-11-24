"""Тестирование маршрутов приложения training."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class TestTrainingUrl(TestCase):
    def setUp(self):
        self.urls = [
            # reverse('reset_learned_words'),
            reverse('active_words'),
            reverse('inactive_words'),
            reverse('learned_words'),
            reverse('word_manager'),
            # reverse('detail'),
            # reverse('edit_word'),
            # reverse('delete_word'),
            # reverse('train_answer'),
            # reverse('train_complete'),
        ]

        self.user = get_user_model().objects.create_user('user', 'user@mail.ru')

        self.client.force_login(self.user)

    def test_urls_for_authorize_client(self):
        """Тестирование маршрутов для авторизованного клиента."""

        for url in self.urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
