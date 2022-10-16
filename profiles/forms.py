from django import forms

from django.contrib.auth import get_user_model

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import Gender, Profile

User = get_user_model()


class ProfileForm(forms.ModelForm):

    date_of_birth = forms.DateField(
        required=False,
        label="Choose Date",
        widget=forms.NumberInput(
            attrs={
                "type": "date",
                "class": "form-control mb-3",
                "placeholder": "Date of Birth",
                "label": "Choose Birth Date",
            }
        ),
    )
    current_address = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Permanent Address",
                "type": "text",
            }
        ),
    )

    gender = forms.ChoiceField(
        required=False,
        choices=Gender,
        widget=forms.Select(
            attrs={"class": "form-control mb-3", "placeholder": "Gender"}
        ),
    )

    city = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "type": "text",
                "placeholder": "Enter City",
            }
        ),
    )

    state_security = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "State Security Number",
                "type": "text",
            }
        ),
    )

    country = CountryField(blank_label="(Select country)")

    class Meta:
        model = Profile
        fields = (
            "date_of_birth",
            "gender",
            "address",
            "profile_pics",
            "city",
            "postal_code",
            "country",
            "state_security",
        )
        widgets = {"country": CountrySelectWidget()}
