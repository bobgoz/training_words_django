"""Тестирование маршрутов приложения training."""

from django.test import SimpleTestCase
from django.urls import resolve, reverse

from training.views import WordCreateView


class TestTrainingUrlsTest(SimpleTestCase):
    def test_url_add_word(self):
        url = reverse("add_word")
        self.assertEqual(resolve(url).func.view_class, WordCreateView)
