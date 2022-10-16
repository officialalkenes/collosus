from django.contrib.auth.models import BaseUserManager

from django.utils.translation import gettext_lazy as _

from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class Manager(BaseUserManager):
    def email_validator(self, email):
        try:
            validate_email(email)
        except ValidationError:
            raise (_("Email Address is not valid"))

    def create_user(
        self, email, username, firstname, lastname, password=None, **extra_fields
    ):
        if not username:
            raise ValueError("User must have a Username submitted")
        if not firstname:
            raise ValueError("User must have a First Name submitted")
        if not lastname:
            raise ValueError("User must have a Last Name submitted")
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError(_("An Email Address must be provided for this account"))
        user = self.model(
            email=email,
            username=username,
            firstname=firstname,
            lastname=lastname,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self, email, username, firstname, lastname, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("An Admin needs superuser permission set as True")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("An Admin needs staff permission set as True")
        if extra_fields.get("is_active") is not True:
            raise ValueError("An Admin needs to be active")

        return self.create_user(
            email, username, firstname, lastname, password, **extra_fields
        )
