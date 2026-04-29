
import re
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
_PHONE_RE = re.compile(r'^\+380\d{9}$')


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
    phone      = forms.CharField(max_length=13, required=False, label='Номер телефону')
    address    = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Вулиця, будинок, квартира, місто'}),
        required=False,
        label='Адреса доставки',
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return ''
        if not _PHONE_RE.match(phone):
            raise ValidationError('Введіть коректний номер у форматі +380XXXXXXXXX (9 цифр після +380).')
        return phone


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = [
        ('card',   'Карткою онлайн'),
        ('cash',   'Готівкою при отриманні'),
        ('postal', 'Накладний платіж'),
    ]

    first_name = forms.CharField(max_length=100, label="Ім'я")
    last_name  = forms.CharField(max_length=100, label='Прізвище')
    email      = forms.EmailField(label='Email')
    phone      = forms.CharField(max_length=20, label='Телефон')
    city       = forms.CharField(max_length=100, label='Місто')
    address    = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Вулиця, будинок, квартира / відділення Нової Пошти'}),
        label='Адреса / відділення',
    )
    payment = forms.ChoiceField(choices=PAYMENT_CHOICES, label='Спосіб оплати', widget=forms.RadioSelect)
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Необов\'язково'}),
        required=False, label='Коментар до замовлення',
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not _PHONE_RE.match(phone):
            raise ValidationError('Введіть номер у форматі +380XXXXXXXXX')
        return phone


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