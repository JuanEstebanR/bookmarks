from django import forms
from django.contrib.auth import get_user_model

from .models import Profile


class LoginForm(forms.Form):
    """
    Form for user to login
    """
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    """
    Form for user to register
    """
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', widget=forms.PasswordInput)

    class Meta:
        """
        Metaclass for UserRegistrationForm
        """
        model = get_user_model()
        fields = ('username', 'first_name', 'email')

    def clean_password2(self):
        """
        Check if password and password2 are the same
        :return:
        """
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clan_email(self):
        """
        Check if email is unique
        :return:
        """
        email = self.cleaned_data.get('email')
        qs = get_user_model().objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError('This email is already registered.')
        return email


class UserEditForm(forms.ModelForm):
    """
    Form for user to edit profile
    """

    class Meta:
        """
        Metaclass for ProfileEditForm
        """
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')


class ProfileEditForm(forms.ModelForm):
    """
    Form for user to edit profile
    """

    class Meta:
        """
        Metaclass for Profile
        """
        model = Profile
        fields = ('date_of_birth', 'photo')
