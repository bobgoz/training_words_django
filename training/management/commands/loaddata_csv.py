import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from training.models import Word

User = get_user_model()


class Command(BaseCommand):
    help = 'Импорт слов из CSV-файла'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file_path',
            type=str,
            help='Путь к CSV-файлу',
            default=r'training/data/words.csv',
        )
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Имя пользователя (по умолчанию: admin)',
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        username = options['username']

        # Получаем или создаём пользователя
        user, created = User.objects.get_or_create(
            username=username,
        )
        if created:
            user.set_password('frikazoid')
            user.save()

        self.stdout.write(f'Пользователь: {user.username}')

        # Читаем CSV
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                skipped = 0

                for row in reader:
                    word_text = row.get('word', '').strip()
                    if not word_text:
                        skipped += 1
                        continue

                    # Проверяем, есть ли уже такое слово у пользователя
                    if Word.objects.filter(user=user, word=word_text).exists():
                        self.stdout.write(
                            f'Слово "{word_text}" уже существует'
                        )
                        skipped += 1
                        continue

                    # Создаём слово
                    Word.objects.create(
                        user=user,
                        word=word_text,
                        definition=row.get('definition', '').strip(),
                    )
                    count += 1
                    self.stdout.write(f'Добавлено: {word_text}')

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Готово! Добавлено: {count}, Пропущено: {skipped}'
                    )
                )

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
