"""Тестирование логики приложения training."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Word

User = get_user_model()


class WordLifecycleViewTest(TestCase):
    """Проверяет жизненный цикл слова через HTTP-интерфейс."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test_user',
            'test@example.ru',
            'password',
        )
        self.word = 'Apple'
        self.slug = self.word.lower()
        self.client.force_login(self.user)
        self.url_add_word = reverse('add_word')
        self.delete_url = reverse('delete_word', kwargs={'slug_word': self.slug})
        self.edit_url = reverse('edit_word', kwargs={'slug_word': self.slug})
        self.detail_url = reverse('detail', kwargs={'slug_word': self.slug})

    def test_user_can_create_edit_and_delete_word(self):
        """Тестирование создания, редактирования и удаления слова."""
        create_response = self.client.post(
            self.url_add_word,
            data=dict(word=self.word, definition='definition'),
        )
        self.assertRedirects(create_response, self.url_add_word)
        self.assertTrue(Word.objects.filter(word=self.word).exists())

        new_data = dict(word='Новое')
        edit_response = self.client.post(self.edit_url, data=new_data)
        self.assertRedirects(edit_response, self.detail_url)
        word = Word.objects.get(slug=self.word.lower())
        self.assertEqual(word.word, new_data['word'])

        delete_response = self.client.post(self.delete_url)
        self.assertRedirects(delete_response, reverse('word_manager'))
        word = Word.objects.filter(word=self.word).exists()
        self.assertFalse(word)
