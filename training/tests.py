from http import HTTPStatus

import pytest
from pytest_lazy_fixtures import lf

LOGIN_URL = lf('login_url')
REGISTER_URL = lf('register_url')
MARK_AS_ACTIVE_URL = lf('mark_as_active_url')
LOGOUT_URL = lf('logout_url')
MARK_AS_INACTIVE_URL = lf('mark_as_inactive_url')
MARK_AS_LEARNED_URL = lf('mark_as_learned_url')
TRAINING_URL = lf('training_url')
TRAINING_NO_ACTIVE_URL = lf('training_no_active_url')
TRAINING_RANDOM_ACTIVE_URL = lf('training_random_active_url')
DETAIL_URL = lf('detail_url')
EDIT_WORD_URL = lf('edit_word_url')
DELETE_WORD_URL = lf('delete_word_url')
SEARCH_URL = lf('search_url')


@pytest.mark.django_db
class TestWordLogic:
    """Тестирование логики тренажера"""

    def test_word_ru(self, client, word_ru):
        """Проверка, что слово относится к категории русских"""
        assert word_ru.language == 'ru', 'Слово не имеет категории "ru".'

    def test_word_en(self, word_en):
        """Проверка, что слово относится к категории английских"""
        assert word_en.language == 'en', 'Слово не имеет категории "en".'


class TestWordUrls:
    """Тестирование роутеров"""

    @pytest.mark.parametrize(
        'name',
        (
            (TRAINING_URL),
            (TRAINING_NO_ACTIVE_URL),
            (TRAINING_RANDOM_ACTIVE_URL),
            (EDIT_WORD_URL),
            (SEARCH_URL),
        ),
    )
    def test_url_for_author_client(self, author_client, name):
        """
        Тестирование роутеров, которые доступны
        только авторизованным клиентам.
        """
        response = author_client.get(name)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize(
        'name',
        (LOGIN_URL,),
    )
    def test_url_for_no_author_client(
        self, author_client, no_author_client, name
    ):
        """
        Тестирование роутеров, которые доступны
        неавторизованным клиентам.
        """

        response = no_author_client.post(name)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize('name', (LOGOUT_URL,))
    def test_url_redirect(self, no_author_client, name):
        """
        Тестирование маршрутов, которые должны перенаправлять
        на другую страницу.
        """
        response = no_author_client.post(name)
        assert response.status_code == HTTPStatus.FOUND

    def test_edit_url(
        self,
        author_client,
        edit_word_url,
        word_ru,
        detail_url,
        form_data,
    ):
        """Дотошное тестирование редактирования слов"""

        response = author_client.get(detail_url)
        word_obj = response.context['word']
        assert word_obj.word == word_ru.word
        # Редактирование слова
        edit_response = author_client.post(edit_word_url, data=form_data)
        assert edit_response.status_code == HTTPStatus.FOUND

        response = author_client.get(detail_url)
        word_obj = response.context['word']
        assert word_obj.word != word_ru.word
