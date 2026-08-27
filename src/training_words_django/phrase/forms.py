from django import forms
from django.utils import timezone

from .models import Phrase


class CreatePhraseForm(forms.ModelForm):
    """Форма для создания словосочетания."""

    class Meta:
        model = Phrase
        fields = (
            "phrase",
            "is_active",
        )


class EditPhraseForm(forms.ModelForm):
    """Форма для редактирования словосочетаний."""

    is_learned = forms.BooleanField(
        widget=forms.HiddenInput(),
        required=False,
        initial=False,
    )
    next_review_date = forms.DateTimeField(
        widget=forms.HiddenInput(),
        required=False,
        initial=False,
    )

    class Meta:
        model = Phrase
        fields = (
            "phrase",
            "is_active",
            "is_learned",
            "next_review_date",
        )

    def clean(self):
        """
        Очистка данных формы.

        Если объект сохраняется
        с флагом is_active, флаг
        is_learned становится False
        для корректного поддержания
        структуры в БД.
        """
        is_active = self.cleaned_data.get('is_active')
        if is_active:
            self.cleaned_data['is_learned'] = False
            self.cleaned_data['next_review_date'] = timezone.now()
        else:
            # Неактивный объект с флагом is_learned = False становится
            # неизученным объектом.
            self.cleaned_data['next_review_date'] = timezone.now()
            self.cleaned_data['is_learned'] = False

        return super().clean()
