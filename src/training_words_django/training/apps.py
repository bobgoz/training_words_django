from django.apps import AppConfig


class TrainingConfig(AppConfig):
    name = "training"

    def ready(self):
        """Переопределение метода для регистрации сигналов."""
        from . import signals  # noqa: F401
