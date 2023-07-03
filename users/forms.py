from django import forms
from django.core.validators import validate_email

from .models import CustomUser


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(validators=[validate_email])

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password', 'email']


class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['phone_number', 'password']


# class ChangePasswordForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
#
#     class Meta:
#         model = CustomUser
#         fields = ['password']

