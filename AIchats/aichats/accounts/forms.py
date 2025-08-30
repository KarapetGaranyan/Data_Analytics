from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class TopUpForm(forms.Form):
    AMOUNT_CHOICES = [
        (100, '100 рублей (50 сообщений)'),
        (200, '200 рублей (100 сообщений)'),
        (500, '500 рублей (250 сообщений)'),
        (1000, '1000 рублей (500 сообщений)'),
        (2000, '2000 рублей (1000 сообщений)'),
    ]

    amount = forms.ChoiceField(
        choices=AMOUNT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Выберите сумму пополнения'
    )