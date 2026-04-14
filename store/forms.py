
import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')


class RegisterForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Підтвердження паролю')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if not _EMAIL_RE.match(email):
            raise ValidationError('Введіть коректний формат email.')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Цей email вже зареєстрований.')
        return email

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Паролі не співпадають.')
        return cleaned


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class ProfileForm(forms.Form):
    GENDER_CHOICES = [
        ('',       '— не вказано —'),
        ('male',   'Чоловік'),
        ('female', 'Жінка'),
        ('other',  'Інше'),
    ]

    first_name = forms.CharField(max_length=150, required=False, label="Ім'я")
    last_name  = forms.CharField(max_length=150, required=False, label='Прізвище')
    gender     = forms.ChoiceField(choices=GENDER_CHOICES, required=False, label='Стать')
    phone      = forms.CharField(max_length=20, required=False, label='Номер телефону')
    address    = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Вулиця, будинок, квартира, місто'}),
        required=False,
        label='Адреса доставки',
    )


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Поточний пароль')
    new_password = forms.CharField(widget=forms.PasswordInput, label='Новий пароль')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='Підтвердження нового паролю')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old = self.cleaned_data['old_password']
        if not self.user.check_password(old):
            raise ValidationError('Поточний пароль невірний.')
        return old

    def clean_new_password(self):
        password = self.cleaned_data['new_password']
        validate_password(password, self.user)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('new_password')
        p2 = cleaned.get('new_password2')
        if p1 and p2 and p1 != p2:
            self.add_error('new_password2', 'Паролі не співпадають.')
        return cleaned