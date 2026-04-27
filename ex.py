from training.models import Word
import re

def detect_language(word):
    if re.search('[а-яА-ЯёЁ]', word):
        return 'ru'
    return 'en'

# Обновить все слова без языка
words = Word.objects.filter(language__isnull=True)
count = words.count()
print(f"Найдено слов для обновления: {count}")

for word in words:
    word.language = detect_language(word.word)
    word.save(update_fields=['language'])

print(f"Обновлено: {count} слов")