# myapp/forms.py

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    verification_code = forms.CharField(widget=forms.PasswordInput)
