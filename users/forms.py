import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import User


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=124, label='Имя')
    surname = forms.CharField(max_length=124, label='Фамилия')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'avatar': 'Аватар',
            'about': 'О себе',
            'phone': 'Телефон',
            'github_url': 'Ссылка на GitHub',
        }
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].required = False
        self.fields['phone'].required = False
        self.fields['github_url'].required = False
        self.fields['about'].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get('phone') or ''
        phone = phone.strip()
        if not phone:
            return None

        m8 = re.fullmatch(r'8(\d{10})', phone)
        m7 = re.fullmatch(r'\+7(\d{10})', phone)

        if not m8 and not m7:
            raise ValidationError('Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX')

        normalized = f'+7{(m8 or m7).group(1)}'

        qs = User.objects.filter(phone=normalized)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Пользователь с таким номером телефона уже существует')

        return normalized

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


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Текущий пароль')
    new_password1 = forms.CharField(widget=forms.PasswordInput, label='Новый пароль')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='Повторите новый пароль')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old = self.cleaned_data.get('old_password')
        if not self.user.check_password(old):
            raise ValidationError('Неверный пароль')
        return old

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password1')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError('Пароли не совпадают')
        return cleaned

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
