from django import forms
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField
from . import models
from . import utils
from . import constants


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


class ContactUsForm(forms.Form):
    name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    phone = PhoneNumberField(required=True, widget=forms.TextInput())
    message = forms.CharField(widget=forms.Textarea, max_length=2000)


class CreateProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('name',)


class EditProjectForm(forms.ModelForm):
    class Meta:
        model = models.Project
        fields = ('name',)


class DateInput(forms.DateInput):
    input_type = 'date'


class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ('date', 'amount', 'comment', 'transaction_type',)
        widgets = {
            'date': DateInput(),
            'transaction_type': forms.Select(choices=constants.TRANSACTION_TYPES)
        }


class MonthsForm(forms.Form):
    months_list = utils.get_months(constants.LAST_MONTHS_COUNT)
    choices = [(month, month.strftime("%B %Y"),) for month in months_list]
    select = forms.ChoiceField(
        choices=tuple(choices),
        widget=forms.Select(attrs={"onchange": 'this.form.submit();'}),
        label='Select month'
    )
