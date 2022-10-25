from django import forms

from django.conf import settings

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import (
    PasswordResetForm,
    PasswordChangeForm,
    SetPasswordForm,
    UserChangeForm,
)


from django.core.exceptions import ValidationError

from profiles.models import Profile

from .models import UserActivity, User


# from django_countries.widgets import CountrySelectWidget


GENDER = (
    ("MALE", "Male"),
    ("FEMALE", "Female"),
)
COUNTRY = (
    ("USA", "USA"),
    ("CANADA", "CANADA"),
    ("FRANCE", "FRANCE"),
    ("UNITED KINGDOM", "UNITED KINGDOM"),
    ("AUSTRALIA", "AUSTRALIA"),
)
CURRENCY_CHOICE = (
    ("USD", "Usd"),
    ("EUR", "Eur"),
    ("CAD", "Cad"),
)


class PwdResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "New Password",
                "id": "form-newpass",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "New Password",
                "id": "form-new-pass2",
            }
        ),
    )


# class LoginForm(forms.Form):
#     email = forms.EmailField(label='Email Address', widget=forms.EmailInput(
#         attrs={'class': 'form-control mb-3', 'placeholder': 'Email Address', 'id': 'form-account'}
#         ))
#     password = forms.CharField(label='Password', widget=forms.PasswordInput(
#         attrs={'class': 'form-control mb-3', 'placeholder': 'Your Password', 'id': 'form-newpass'}
#     ))
#     class Meta:
#         model = User
#         fields = ['account_number', 'password']


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Email",
                "id": "form-email",
            }
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Your Password",
                "id": "form-newpass",
            }
        ),
    )


class PwdChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Old Password",
                "id": "form-oldpass",
            }
        ),
    )
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "New Password",
                "id": "form-newpass",
            }
        ),
    )
    new_password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "New Password",
                "id": "form-new-pass2",
            }
        ),
    )


class PwdResetForm(PasswordResetForm):

    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Email",
                "id": "form-email",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        test = User.objects.filter(email=email)
        if not test:
            raise forms.ValidationError(
                "Unfortunatley we can not find that email address"
            )
        return email


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=100,
        help_text="Required",
        error_messages={"required": "Sorry, you will need an email"},
    )

    username = forms.CharField(
        label="Enter Username", min_length=4, max_length=50, help_text="Required"
    )
    firstname = forms.CharField(
        label="Enter Your First Name", min_length=4, max_length=50, help_text="Required"
    )
    lastname = forms.CharField(
        label="Enter Your Other Name/Names",
        min_length=4,
        max_length=50,
        help_text="Required",
    )
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Repeat password", widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "username",
            "firstname",
            "lastname",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control mb-3", "placeholder": "Username"}
        )
        self.fields["email"].widget.attrs.update(
            {
                "class": "form-control mb-3",
                "placeholder": "E-mail",
                "name": "email",
                "id": "id_email",
            }
        )
        self.fields["firstname"].widget.attrs.update(
            {
                "class": "form-control mb-3",
                "placeholder": "Your First Name",
                "name": "firstname",
                "id": "id_firstname",
            }
        )
        self.fields["lastname"].widget.attrs.update(
            {
                "class": "form-control mb-3",
                "placeholder": "Other Names",
                "name": "lastname",
                "id": "id_lastname",
            }
        )

        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Repeat Password"}
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):

    username = forms.CharField(
        label="Username",
        min_length=4,
        max_length=50,
        disabled=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
                "type": "text",
            }
        ),
    )

    firstname = forms.CharField(
        label="firstname",
        min_length=4,
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "firstname",
                "type": "text",
            }
        ),
    )

    lastname = forms.CharField(
        label="Lastname",
        min_length=4,
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Lastname",
                "type": "text",
            }
        ),
    )

    email = forms.EmailField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Old Password",
                "type": "email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("firstname", "lastname", "email", "username")


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "firstname",
            "lastname",
        ]


class WalletUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("btc_wallet",)
