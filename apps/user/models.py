from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from django.db import models
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from .managers import Manager


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
