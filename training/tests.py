from http import HTTPStatus

import pytest
from django.urls import reverse

from training.models import Word


@pytest.mark.django_db
class TestWordLogic:
    """Тестирование логики тренажера"""

    def test_word_ru(self, client, word_ru):
        """Проверка, что слово относится к категории русских"""
        assert word_ru.language == "ru", 'Слово не имеет категории "ru".'

    def test_word_en(self, word_en):
        """Проверка, что слово относится к категории английских"""
        assert word_en.language == "en", 'Слово не имеет категории "en".'

    def test_create_word(self, author, auth_client, form_data, create_url):
        """Тестирование логики добавления слова."""
        response = auth_client.post(create_url, form_data)
        assert response.status_code == HTTPStatus.FOUND
        word = Word.objects.get(
            user=author.id,
            word="Слово",
        )
        assert word.word == form_data["word"].title()
        assert word.user == form_data["user"]

    def test_not_active_url(
        self,
        auth_client,
        word_mass_create_noactive,
        noactive_url,
    ):
        """Тестирование логики страницы с неактивными словами."""
        response = auth_client.get(noactive_url)
        assert response.status_code == HTTPStatus.OK
        assert Word.objects.filter(
            is_active=False,
        ).exists()
        words = response.context.get("words")
        assert words is not None
        assert len(words) == 10
        # Получение одного объекта слова и изменение поля is_learn на True
        word = Word.objects.get(pk=1)
        word.is_learned = True
        word.save()

        # Проверка, что данного объекта нет в контексте страницы noactive
        response2 = auth_client.get(noactive_url)
        words2 = response2.context.get("words")

        learned_in_context = [w for w in words2 if w.is_learned]
        assert len(learned_in_context) == 0

        response = auth_client.get(noactive_url)
        words = response2.context.get("words")

        # И общее количество слов уменьшилось на 1
        assert len(words) == 9


@pytest.mark.django_db
class TestWordUrls:
    """Тестирование роутеров"""

    TRAINING_URLS = (
        "add_word",
        "active_words",
        "inactive_words",
        "learned_words",
        "training_setup",
    )

    @pytest.mark.parametrize("name", TRAINING_URLS)
    def test_url_for_auth_client(self, auth_client, name):
        """
        Тестирование роутеров приложения training
        для  авторизованного пользователя.
        """
        url = reverse(name)
        response = auth_client.get(url)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize("name", TRAINING_URLS)
    def test_url_for_anonim_client(self, client, name):
        """
        Тестирование роутеров приложения training
        для неавторизованного пользователя.
        """
        url = reverse(name)
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND

    def test_edit_url(
        self,
        auth_client,
        edit_word_url,
        word_ru,
        word_detail_url,
        form_data,
    ):
        """Тестирование редактирования слов"""

        response = auth_client.get(word_detail_url)
        word_obj = response.context["word"]
        assert word_obj.word == word_ru.word
        # Редактирование слова
        edit_response = auth_client.post(edit_word_url, data=form_data)
        assert edit_response.status_code == 302
        response = auth_client.get(word_detail_url)
        word_obj = response.context["word"]
        assert word_obj.word != word_ru.word
