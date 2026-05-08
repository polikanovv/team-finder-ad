from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
            'github_url': 'Ссылка на GitHub',
            'status': 'Статус',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'status': forms.Select(choices=[('open', 'Открыт'), ('closed', 'Закрыт')]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['github_url'].required = False

    def clean_github_url(self):
        url = (self.cleaned_data.get('github_url') or '').strip()
        if not url:
            return url
        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:
            raise ValidationError('Введите корректную ссылку')
        if 'github.com' not in url:
            raise ValidationError('Ссылка должна вести на GitHub (github.com)')
        return url
