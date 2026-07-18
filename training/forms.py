"""Модуль содержащий  формы Django."""

from django import forms
from django.utils import timezone

from .constants import COUNT_INITIAL_VALUE, NUMBER_OF_WORD
from .models import Word


class CreateWordForm(forms.ModelForm):
    """Форма для создания слова."""

    class Meta:
        model = Word
        fields = (
            "word",
            "definition",
            "example",
            "image",
            "is_active",
        )


class EditWordForm(forms.ModelForm):
    """Форма редактирования слова."""

    word = forms.CharField(
        label="Слово",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Введите слово"}
        ),
    )

    definition = forms.CharField(
        label="Определение",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Определение слова",
            }
        ),
    )

    example = forms.CharField(
        label="Пример использования",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Пример использования слова",
            }
        ),
    )

    is_active = forms.BooleanField(
        label="Активное слово",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    is_learned = forms.BooleanField(
        label="Изученное слово",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    image = forms.ImageField(
        label="Изображение",
        required=False,
        widget=forms.FileInput(attrs={"class": "form-control"}),
    )

    next_review_date = forms.DateTimeField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def clean(self):
        """Очищает данные формы.

        Нельзя использовать два флага
        is_active и is_learned одновременно.

        Если Пользователь выбрал слово как активное,
        сбрасывается дата следующей тренировки.
        """
        is_active = self.cleaned_data.get("is_active")
        is_learned = self.cleaned_data.get("is_learned")

        if is_active and is_learned:
            raise forms.ValidationError(
                "Слово не может быть одновременно активным и изученным.",
            )
        if is_active:
            self.cleaned_data["next_review_date"] = timezone.now()

        return super().clean()

    def save(self, commit=True):
        """Удаление картинки."""
        instance = super().save(commit=False)
        if self.cleaned_data.get("delete_image") and instance.image:
            # Если картинка есть в хранилище:
            if instance.image.storage.exists(instance.image.name):
                instance.image.delete()
            # Если в хранилище нет, но есть название в БД
            else:
                instance.image = None
        return super().save(commit)

    class Meta:
        model = Word
        fields = (
            "word",
            "definition",
            "example",
            "is_active",
            "is_learned",
            "image",
            "next_review_date",
        )

    def __init__(self, *args, **kwargs):
        """Добавление поля формы, если есть изображение."""
        super(EditWordForm, self).__init__(*args, **kwargs)
        if self.instance.image:
            self.fields["delete_image"] = forms.BooleanField(
                label="Удалить картинку",
                required=False,
                widget=forms.CheckboxInput(),
            )


class TrainingSettingsForm(forms.Form):
    """Форма настройки тренировки."""

    COUNT_CHOICES = [(i, str(i)) for i in NUMBER_OF_WORD]

    WORD_TYPE_CHOICES = [
        ("all", "Активные"),
        ("learned", "Изученные"),
    ]

    word_type = forms.ChoiceField(
        choices=WORD_TYPE_CHOICES,
        widget=forms.RadioSelect,
        initial=WORD_TYPE_CHOICES[0],
        label="Тип слов",
    )

    count = forms.TypedChoiceField(
        choices=COUNT_CHOICES,
        initial=COUNT_INITIAL_VALUE,
        coerce=int,
        label="Количество слов",
        help_text="Сколько слов включить в тренировку? ",
    )
    is_arbitrary = forms.BooleanField(
        label="В произвольном порядке",
        help_text="Если не выбрано, слова будут отображаться в упорядоченном "
        "порядке.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        """Динамическое добавление полей."""
        super().__init__(*args, **kwargs)
        if Word.objects.filter(language="en").exists():
            self.fields["only_en_words"] = forms.BooleanField(
                label="Только английские слова",
                help_text="Начни тренировку английских слов",
                required=False,
            )
            self.fields["only_ru_words"] = forms.BooleanField(
                label="Только русские слова",
                help_text="Начни тренировку русских слов",
                required=False,
            )

    def clean(self):
        """Очистка данных формы."""
        only_en_words = self.cleaned_data.get("only_en_words")
        only_ru_words = self.cleaned_data.get("only_ru_words")
        if only_en_words and only_ru_words:
            raise forms.ValidationError(
                "Выберите либо русские, либо английские слова!",
            )
        return super().clean()
