from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Phrase

User = get_user_model()


class TestPhraseUrl(TestCase):
    """Тестирование маршрутов приложения phrase"""

    def setUp(self):
        self.urls = [
            'add_phrase',
            'phrase_manager',
            'active_phrases',
            'inactive_phrases',
            'learned_phrases',
        ]
        username = 'test_username'
        password = 'test_password'
        self.user = User.objects.create_user(username, password=password)
        self.client.login(username=username, password=password)
        self.phrase = Phrase.objects.create(
            phrase='Пушечный удар',
            user=self.user,
        )
        self.phrase_data = dict(phrase='пушечный удар')

    def test_urls(self):
        """Тестирование юрлов."""
        for url in self.urls:
            url = reverse(url)
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_create_phrase(self):
        """Тестирование создания объекта."""
        url_add_phrase = reverse(self.urls[0])
        response = self.client.post(url_add_phrase, self.phrase_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Phrase.objects.filter(**self.phrase_data).exists())

    def test_detail_url(self):
        """Тестирование юрла для детального отображения."""
        url = reverse('phrase_detail', kwargs={"pk_phrase": self.phrase.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
