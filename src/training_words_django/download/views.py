import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views import View

from training.models import Word


class DownloadView(LoginRequiredMixin, View):
    """Загрузка файла"""

    def post(self, request):
        words = Word.words.is_active(request.user)[:10]

        words_without_definition = [
            word.word for word in words if not word.definition
        ]
        if words_without_definition:
            messages.warning(
                request,
                'Для этих слов: '
                f'{' ,'.join(words_without_definition)} '
                'нет определения! '
                'Рекомендовано добавить определение.',
            )
            return redirect('active_words')

        current_date = timezone.now().date()

        filename = f'words_{request.user.username}_{current_date}'

        response = HttpResponse(
            headers={
                'Content-Type': 'application/csv; charset=utf-8',
                'Content-Disposition': f'attachment; filename={filename}.csv',
            },
        )
        response.write('\ufeff')

        # CSV
        writer = csv.writer(response)
        writer.writerow(['Слово', 'Определение'])

        for word in words:
            writer.writerow([f'{word.word}\t{word.definition}'])
        return response
