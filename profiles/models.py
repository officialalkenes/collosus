from msilib.schema import Error

from django.conf import settings

from django.db import models

from django.utils.translation import gettext_lazy as _

from django_countries.fields import CountryField

from .utils import get_referral_code, user_directory_path


class Gender(models.TextChoices):
    MALE = "Male", _("Male")
    FEMALE = "Female", _("Female")
    OTHER = "Other", _("Other")


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    balance = models.DecimalField(default=5.00, max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(default=0)
    date_of_birth = models.DateField(
        verbose_name=_("Date of Birth"), null=True, blank=True
    )
    gender = models.CharField(
        max_length=20, choices=Gender.choices, default=Gender.OTHER
    )
    occupation = models.CharField(max_length=200, blank=True)
    profile_pics = models.ImageField(upload_to=user_directory_path, blank=True)
    address = models.CharField(max_length=250, blank=True)
    btc_wallet = models.CharField(
        max_length=100, blank=True, verbose_name=_("Bitcoin Address")
    )
    # eth_wallet = models.CharField(
    #     max_length=100, blank=True, verbose_name=_("Ethereum Address")
    # )
    # trx_wallet = models.CharField(
    #     max_length=100, blank=True, verbose_name=_("Tron Address")
    # )

    recommended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recomendation",
        blank=True,
        null=True,
    )

    code = models.CharField(
        max_length=13, verbose_name=_("Referral Code"), blank=True, unique=True
    )

    country = CountryField(blank=True, default="US")

    profile_pics = models.ImageField(upload_to="image", blank=True, null=True)

    city = models.CharField(
        max_length=100, default="New York", help_text="Change to your city"
    )

    postal_code = models.PositiveIntegerField(
        blank=True, null=True, verbose_name=_("City Postal Code")
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")

    def get_recommended_profiles(self):
        qs = Profile.objects.all()
        profile_recommend = [p for p in qs if p.recommended_by == self.user]
        return profile_recommend

    @property
    def get_total_ref_balance(self):
        balance = len(self.get_recommended_profiles())
        return balance * 50.00

    def __str__(self) -> str:
        return f"{self.user.email}"

    def save(self, *args, **kwargs):
        if self.code == "":
            code = get_referral_code()
            try:
                old_ref = Profile.objects.filter(code=code)
                if old_ref:
                    code = get_referral_code()
            except Error as e:
                print(e)
            self.code = code
        return super().save(*args, **kwargs)


# To be stored in router.py
class LegacyRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "legacy":
            return "legacy"
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "legacy":
            return "legacy"
        return None


# Add router to settings.py
DATABASE_ROUTER = "app.router.LegacyRouter"


# Run this code on terminal after
# py manage.py inspectdb --databse=legacy > models.py

"""

    Create a custom management command and

"""

# Dump data command

# python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission --indent 2 > dump.json
