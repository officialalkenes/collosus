from email.policy import default
import random
from sqlite3 import TimestampFromTicks
import string
import uuid
from django.utils.text import slugify

from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField


class TimeStampedUUIDModels(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class InvestmentType(models.TextChoices):
    Basic = "Basic", _("Basic Plan")
    Limited = "Limited", _("Limited Plan")
    Unlimited = "Unlimited", _("Unlimited Plan")
    IRA = "Individual Retirement Account", _("Individual Retirement Account Plan")


class Status(models.TextChoices):
    Pending = "Pending", _("Pending")
    Processing = "Processing", _("Processing")
    Successful = "Successful", _("Successful")


class PaymentMethod(models.TextChoices):
    BTC = "Bitcoin Address", _("Bitcoin Address")
    ETH = "Ethereum Address", _("Ethereum Address")
    TRX = "Tron Address", _("Tron Address")


class InvestmentTypes(models.Model):
    investment_type = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Investment Type"),
        choices=InvestmentType.choices,
    )

    def __str__(self):
        return f"{self.investment_type}"

    class Meta:
        verbose_name_plural = "Investment Types"
        verbose_name = "Investment Type"


class Investment(TimeStampedUUIDModels):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="investment"
    )
    trxid = models.CharField(max_length=10, blank=True)
    investment_type = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Investment Type"),
        choices=InvestmentType.choices,
    )
    amount = models.DecimalField(blank=True, max_digits=8, decimal_places=2)
    percentage = models.DecimalField(
        blank=True, null=True, max_digits=3, decimal_places=2
    )
    total_percentage = models.DecimalField(default=0.00, max_digits=3, decimal_places=2)
    total_days = models.PositiveIntegerField(blank=True, null=True)
    profit = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.Pending
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.user.username} - {self.investment_type}"

    def save(self, *args, **kwargs):
        N = 10
        if self.trxid == "":
            self.trxid = "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(N)
            )

        if self.investment_type == "Basic":
            self.amount = 200
            self.total_days = 7
            self.percentage = 0.15

        if self.investment_type == "Limited":
            self.total_days = 7
            self.percentage = 0.20

        if self.investment_type == "Unlimited":
            self.total_days = 7
            self.percentage = 0.20

        if self.investment_type == "Individual Retirement Account":
            self.amount = 500
            self.total_days = 14
            self.percentage = 0.35

        if self.status == Status.Successful and self.total_days is not None:
            total_days = int(self.total_days)
            self.start_date = datetime.today().strftime("%Y-%m-%d")
            self.end_date = datetime.today() + timedelta(days=total_days)

        return super().save(*args, **kwargs)

    @property
    def total_profit(self):
        total_profit = self.percentage * self.amount
        return total_profit

    # @property
    # def total_profit(self):
    #     total_profit = self.percentage * self.amount
    #     return total_profit

    def get_total_return(self):
        percent_amount = self.amount * self.total_percentage
        total = self.amount + percent_amount
        return total


class Deposit(TimeStampedUUIDModels):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deposit"
    )
    trx = models.CharField(max_length=10, blank=True, verbose_name=_("Transaction Id"))
    slug = models.SlugField(max_length=8, blank=True)
    payment = models.CharField(
        max_length=30,
        verbose_name=_("Payment Method"),
        choices=PaymentMethod.choices,
        default=PaymentMethod.BTC,
    )
    proof = models.ImageField(blank=True)
    wallet_address = models.CharField(
        max_length=100, verbose_name=_("Receiving Wallet Address"), blank=True
    )
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="Enter Amount in Usd Ratio"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.Pending
    )

    def save(self, *args, **kwargs):
        if self.payment == PaymentMethod.BTC:
            self.wallet_address = "asderdhs16w2sw6e3w7"
        elif self.payment == PaymentMethod.ETH:
            self.wallet_address = "124swssfhwaahaha"
        else:
            self.wallet_address = "cscswe88e999wesu"

        N = 8
        if self.trx == "":
            self.trx = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(N)
            )
        if self.slug == "":
            self.slug = slugify(self.trx)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("investicon:update-deposit", kwargs={"slug": self.slug})

    def get_admin_url(self):
        return reverse("investicon:admin-deposit-update", kwargs={"slug": self.slug})


class Withdrawal(TimeStampedUUIDModels):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="withdrawal"
    )
    slug = models.SlugField(max_length=8, blank=True)
    trx = models.CharField(max_length=10, blank=True, verbose_name=_("Transaction Id"))
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="Enter Amount in Usd Ratio"
    )
    address = models.CharField(
        max_length=100,
        verbose_name=_("Receiving Wallet Address"),
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.Pending
    )

    def save(self, *args, **kwargs):
        N = 10
        if not self.trx:
            self.trx = "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(N)
            )
        if self.slug == "":
            self.slug = slugify(self.trx)
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("investicon:update-withdrawal", kwargs={"slug": self.slug})

    def get_admin_url(self):
        return reverse("investicon:admin-deposit-update", kwargs={"slug": self.slug})


class Portfolio(TimeStampedUUIDModels):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="portfolio"
    )
    balance = models.DecimalField(default=5.00, max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        N = 8
        self.trx = "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(N)
        )
        return super().save(*args, **kwargs)


class PaidBy(models.Model):
    name = models.CharField(max_length=40, verbose_name=_("Preferred Name"))
    amount = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name=_("Amount Paid")
    )
    country = CountryField(blank=True, default="US")
