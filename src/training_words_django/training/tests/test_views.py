"""Тестирование маршрутов приложения training."""

from django.test import SimpleTestCase
from django.urls import resolve, reverse
from training.views import (
    DeleteWordView,
    DetailWordView,
    EditWordView,
    ResetLearnedWordsView,
    SearchView,
    ShowActiveWordsView,
    ShowInactiveWordsView,
    ShowLearnedView,
    TrainAnswerView,
    TrainCardView,
    TrainCompleteView,
    TrainingSetupView,
    WordCreateView,
    WordManagerView,
)


class TrainingUrlsTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        cls.args = (1,)

    def test_url_add_word_resolve_view(self):
        url = reverse('add_word')
        self.assertEqual(resolve(url).func.view_class, WordCreateView)

    def test_active_words_resolve_view(self):
        url = reverse('active_words')
        self.assertEqual(resolve(url).func.view_class, ShowActiveWordsView)

    def test_inactive_words_resolve_view(self):
        url = reverse('inactive_words')
        self.assertEqual(resolve(url).func.view_class, ShowInactiveWordsView)

    def test_learned_words_resolve_view(self):
        url = reverse('learned_words')
        self.assertEqual(resolve(url).func.view_class, ShowLearnedView)

    def test_detail_resolve_view(self):
        url = reverse('detail', args=self.args)
        self.assertEqual(resolve(url).func.view_class, DetailWordView)

    def test_edit_word_resolve_view(self):
        url = reverse('edit_word', args=self.args)
        self.assertEqual(resolve(url).func.view_class, EditWordView)

    def test_delete_word_resolve_view(self):
        url = reverse('delete_word', args=self.args)
        self.assertEqual(resolve(url).func.view_class, DeleteWordView)

    def test_word_manager_resolve_view(self):
        url = reverse('word_manager')
        self.assertEqual(resolve(url).func.view_class, WordManagerView)

    def test_training_setup_resolve_view(self):
        url = reverse('training_setup')
        self.assertEqual(resolve(url).func.view_class, TrainingSetupView)

    def test_reset_learned_words_resolve_view(self):
        url = reverse('reset_learned_words')
        self.assertEqual(resolve(url).func.view_class, ResetLearnedWordsView)

    def test_search_words_resolve_view(self):
        url = reverse('search')
        self.assertEqual(resolve(url).func.view_class, SearchView)

    def test_train_answer_words_resolve_view(self):
        url = reverse('train_answer')
        self.assertEqual(resolve(url).func.view_class, TrainAnswerView)

    def test_train_complete_words_resolve_view(self):
        url = reverse('train_complete')
        self.assertEqual(resolve(url).func.view_class, TrainCompleteView)

    def test_train_card_resolve_view(self):
        url = reverse('train_card')
        self.assertEqual(resolve(url).func.view_class, TrainCardView)
