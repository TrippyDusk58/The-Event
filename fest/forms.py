from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from fest.models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email','subject', 'message']

class RegisterForm(UserCreationForm):
    class Meta:
        model = User  # Using Django's built-in User model
        fields = ['username', 'email', 'password1', 'password2']  # Registration fields