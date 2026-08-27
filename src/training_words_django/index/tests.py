from django.test import SimpleTestCase
from django.urls import reverse


class TestIndex(SimpleTestCase):
    """Тестирование приложения index"""

    def test_url(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
