from gettext import gettext


from django.utils.translation import gettext_lazy as _

from django import forms
from django_countries.widgets import CountrySelectWidget
from django_countries.fields import CountryField

from .models import Deposit, Investment, PaymentMethod, Withdrawal

InvestmentTypes = (
    ("Basic"),
    _("Basic Plan"),
    ("Limited"),
    _("Limited Plan"),
    ("Unlimited"),
    _("Unlimited Plan"),
    ("Individual Retirement Account"),
    _("Individual Retirement Account Plan"),
)


class BasicInvestmentForm(forms.ModelForm):
    amount = forms.DecimalField(max_value=201, min_value=200)

    class Meta:
        model = Investment
        fields = ("amount",)


class LimitedInvestmentForm(forms.ModelForm):
    amount = forms.DecimalField(max_value=999, min_value=300)

    class Meta:
        model = Investment
        fields = ("amount",)

    def save(self, *args, **kwargs):
        self.instance.investment = 2
        return super().save(*args, **kwargs)


class DepositForm(forms.ModelForm):
    amount = forms.DecimalField()
    # payment = forms.ChoiceField(choices=PaymentMethod, widget=forms.RadioSelect(
    #     attrs={'class':'radio_1', 'name': 'name2'}))

    class Meta:
        model = Deposit
        fields = ["amount", "payment"]


class Withdrawal(forms.Form):
    amount = forms.DecimalField()
    payment = forms.ChoiceField(
        choices=PaymentMethod,
        widget=forms.RadioSelect(attrs={"class": "radio_1", "name": "name2"}),
    )

    class Meta:
        model = Withdrawal
        fields = ["amount", "payment"]


class UnlimitedInvestmentForm(forms.ModelForm):
    amount = forms.DecimalField(min_value=1000)

    class Meta:
        model = Investment
        fields = ("amount",)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class IraInvestmentForm(forms.ModelForm):
    amount = forms.DecimalField(min_value=500)

    class Meta:
        model = Investment
        fields = ("amount",)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class DepositProofForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = ("proof",)


class TransferInvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = (
            "user",
            "trxid",
            "investment_type",
            "amount",
            "percentage",
            "total_percentage",
            "total_days",
            "profit",
            "status",
            "start_date",
            "end_date",
            "completed",
        )


# class TransferDepositForm(forms.Modelform):
#     amount = forms.DecimalField(max_value=5000,
#                                 help_text=_("Enter Amount here"))

#     investment = forms.formset_factory()

#     class Meta:
#         model = Deposit
#         fields = "__all__"


class UpdateDepositForm(forms.ModelForm):
    class Meta:
        model = Deposit
        fields = (
            "user",
            "trx",
            "payment",
            "proof",
            "wallet_address",
            "amount",
            "status",
        )
