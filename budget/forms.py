from django import forms
from django.contrib.auth.models import User
from . import models


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

    def clean_password_confirm(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password_confirm']:
            raise forms.ValidationError('Password don\'t match')
        return cd['password']


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('name', )


class EditProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('name', )
