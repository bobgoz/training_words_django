"""Интеграционные тесты сценариев тренировки."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from training.models import TrainingSession, Word

User = get_user_model()


class TrainingFlowViewTest(TestCase):
    """Проверяет полный цикл тренировки слов через HTTP."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="test-password-4826",
        )
        self.client.force_login(self.user)

        self.training_setup_url = reverse("training_setup")
        self.train_card_url = reverse("train_card")
        self.train_answer_url = reverse("train_answer")
        self.train_complete_url = reverse("train_complete")

        Word.objects.bulk_create(
            [
                Word(
                    user=self.user,
                    word=f"word{number}",
                    language="en",
                    is_active=True,
                )
                for number in range(10)
            ],
        )

    def user_completes_word_training(self):
        """Пользователь проходит тренировку, а результаты сохраняются."""
        setup_response = self.client.post(
            self.training_setup_url,
            data={
                "word_type": "words",
                "count": 10,
            },
        )

        self.assertRedirects(setup_response, self.train_card_url)

        training_ids = self.client.session["training_words"]["ids"]
        self.assertEqual(len(training_ids), 10)

        for index, word_id in enumerate(training_ids):
            is_known = index < 3

            answer_response = self.client.post(
                self.train_answer_url,
                data={
                    "word_id": word_id,
                    "is_known": str(is_known).lower(),
                },
            )

            expected_url = (
                self.train_complete_url
                if index == len(training_ids) - 1
                else self.train_card_url
            )
            self.assertRedirects(answer_response, expected_url)

        complete_response = self.client.get(self.train_complete_url)

        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(complete_response.context["total_words"], 10)
        self.assertEqual(complete_response.context["correct_count"], 3)
        self.assertEqual(complete_response.context["incorrect_count"], 7)
        self.assertEqual(complete_response.context["accuracy"], 30.0)

        training_session = TrainingSession.objects.get(user=self.user)
        self.assertIsNotNone(training_session.ended_at)
        self.assertEqual(training_session.total_words, 10)
        self.assertEqual(training_session.correct_words, 3)
        self.assertEqual(training_session.incorrect_words, 7)

        self.assertEqual(
            Word.objects.filter(
                user=self.user, is_learned=True, is_active=False
            ).count(),
            3,
        )
        self.assertEqual(
            Word.objects.filter(
                user=self.user, is_learned=False, is_active=True
            ).count(),
            7,
        )

        session = self.client.session
        self.assertNotIn("training_words", session)
        self.assertNotIn("training_session_id", session)
