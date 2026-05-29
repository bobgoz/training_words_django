from django import forms
from django.utils import timezone

from .constants import (
    COUNT_INITIAL_VALUE,
    COUNT_MAX_VALUE,
    COUNT_MIN_VALUE,
)
from .models import Word


class CreateWordForm(forms.ModelForm):
    """Форма для создания слова"""

    class Meta:
        model = Word
        fields = (
            'word',
            'definition',
            'example',
            'image',
            'is_active',
        )
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'word': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'autofocus': True,
                    'autocomplete': 'off',
                    'placeholder': 'Введите слово',
                }
            ),
        }


class EditWordForm(forms.ModelForm):
    """Форма редактирования слова"""

    word = forms.CharField(
        label='Слово',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Введите слово'}
        ),
    )

    definition = forms.CharField(
        label='Определение',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Определение слова',
            }
        ),
    )

    example = forms.CharField(
        label='Пример использования',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Пример использования слова',
            }
        ),
    )

    is_active = forms.BooleanField(
        label='Активное слово',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    is_hard = forms.BooleanField(
        label='Сложное слово',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    is_learned = forms.BooleanField(
        label='Изученное слово',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    image = forms.ImageField(
        label='Изображение',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
    )

    repetition_count = forms.IntegerField(
        label='Количество повторений',
        required=False,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'readonly': True,
            }
        ),
    )

    next_review_date = forms.DateTimeField(
        label='Следующее повторение',
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            },
        ),
        initial=timezone.now(),
        required=False,
    )

    next_review_date = forms.DateTimeField(
        label='Следующее повторение',
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',
            },
        ),
        initial=timezone.now(),
        required=False,
    )

    class Meta:
        model = Word
        fields = (
            'word',
            'definition',
            'example',
            'is_active',
            'is_hard',
            'is_learned',
            'image',
            'repetition_count',
            'next_review_date',
        )


class TrainingSettingsForm(forms.Form):
    """Форма настройки тренировки"""

    WORD_TYPE_CHOICES = [
        ('all', 'Активные слова'),
        ('hard', 'Только сложные'),
        ('learned', 'Только изученные'),
        ('random', 'Случайные'),
    ]

    word_type = forms.ChoiceField(
        choices=WORD_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial=WORD_TYPE_CHOICES[0],
        label='Тип слов',
    )

    count = forms.IntegerField(
        min_value=COUNT_MIN_VALUE,
        max_value=COUNT_MAX_VALUE,
        initial=COUNT_INITIAL_VALUE,
        label='Количество слов',
        help_text=(
            'Сколько слов включить в тренировку? '
            f'({COUNT_MIN_VALUE}-{COUNT_MAX_VALUE})',
        ),
    )
