from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.db import models
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)


from django.db.models.functions import Now
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .managers import Manager

from profiles.models import Profile
from investment.models import Portfolio


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name=_("Email Address"))
    username = models.CharField(max_length=255, unique=True, verbose_name=_("Username"))
    firstname = models.CharField(
        max_length=255, unique=True, verbose_name=_("First Name")
    )
    lastname = models.CharField(
        max_length=255, unique=True, verbose_name=_("Last Name")
    )
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    objects = Manager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "firstname", "lastname"]

    def __str__(self) -> str:
        return f"{self.email}"

    def get_absolute_url(self):
        return reverse("accounts:user-update", args=[str(self.id)])

    @property
    def get_fullname(self):
        return f"{self.firstname.title()} {self.lastname.title()}"

    def get_shortname(self):
        return f"{self.username}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    # def get_absolute_url(self):
    #     return reverse("accounts:profile-updating", args=[str(self.id)])


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, db_index=True, null=True, blank=True)
    login = models.DateTimeField(auto_now_add=True)
    logout = models.DateTimeField(null=True, default=None)


class LoginAttempt(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    login_attempts = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "user: {}, attempts: {}".format(self.user.email, self.login_attempts)


@receiver(post_save, sender=User)
def post_save_profile_receiver(sender, instance, created, **kwargs):
    if created:
        Portfolio.objects.create(user=instance)
        Profile.objects.create(user=instance)


@receiver(user_logged_in)
def register_login(sender, user, request, **kwargs):
    UserActivity.objects.create(user=user, session_key=request.session.session_key)


@receiver(user_logged_out)
def register_logout(sender, user, request, **kwargs):
    UserActivity.objects.filter(
        user=user, session_key=request.session.session_key
    ).update(logout=Now())


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    return "user {} logged in through page {}".format(
        user.username, request.META.get("HTTP_REFERER")
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    return "user {} logged in failed through page {}".format(
        credentials.get("username"), request.META.get("HTTP_REFERER")
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    return "user {} logged out through page {}".format(
        user.username, request.META.get("HTTP_REFERER")
    )
