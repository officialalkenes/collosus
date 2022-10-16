from datetime import date, datetime

from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)

from django.db.models.functions import Now
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from django.utils.text import slugify

from .models import *

# from profiles.models import Profile
# from investment.models import Portfolio


# @receiver(post_save, sender=User)
# def post_save_profile_receiver(sender, instance, created, **kwargs):
#     if created:
#         Portfolio.objects.create(
#             user=instance)
#         Profile.objects.create(
#                 user=instance)


# @receiver(user_logged_in)
# def register_login(sender, user, request, **kwargs):
#     UserActivity.objects.create(user=user, session_key=request.session.session_key)


# @receiver(user_logged_out)
# def register_logout(sender, user, request, **kwargs):
#     UserActivity.objects.filter(
#         user=user, session_key=request.session.session_key
#     ).update(logout=Now())


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
