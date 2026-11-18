from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking, ContactMessage


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'form-input',
                'placeholder': self.fields[field_name].label,
            })


class BookingForm(forms.ModelForm):
    """Форма бронирования объекта"""
    class Meta:
        model = Booking
        fields = ['check_in_date', 'check_out_date', 'base_guests_count', 'extra_guests_count']
        widgets = {
            'check_in_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'id': 'check_in',
                'required': True,
            }),
            'check_out_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'id': 'check_out',
                'required': True,
            }),
            'base_guests_count': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 20,
                'required': True,
            }),
            'extra_guests_count': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 0,
                'max': 2,
                'value': 0,
            }),
        }

    def clean_extra_guests_count(self):
        extra = self.cleaned_data.get('extra_guests_count', 0)
        if extra > 2:
            raise forms.ValidationError('Максимум 2 дополнительных спальных места')
        return extra

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in_date')
        check_out = cleaned_data.get('check_out_date')
        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError('Дата выезда должна быть позже даты заезда')
            from datetime import date
            if check_in < date.today():
                raise forms.ValidationError('Дата заезда не может быть в прошлом')
        return cleaned_data


class ContactForm(forms.ModelForm):
    """Форма обратной связи на странице Контакты"""
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Ваш email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 900 000-00-00'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Тема сообщения'}),
            'message': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Ваше сообщение', 'rows': 5}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not phone.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise forms.ValidationError('Введите телефон в формате +7 900 000-00-00')
        return phone

    def clean_message(self):
        message = self.cleaned_data.get('message', '')
        if len(message) < 10:
            raise forms.ValidationError('Сообщение должно содержать минимум 10 символов')
        return message


class SubscriptionForm(forms.Form):
    """Форма подписки в футере"""
    email = forms.EmailField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ваш email',
            'required': True,
        })
    )