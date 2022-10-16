from datetime import timedelta

from django.conf import settings

from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site

from django.http import BadHeaderError, HttpResponse

from django.shortcuts import render, redirect, get_object_or_404

from django.template.loader import render_to_string

from django.utils import timezone
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.views.generic import FormView, CreateView, UpdateView

from .models import LoginAttempt, User, UserActivity

from .decorators import unauthenticated_user
from .forms import LoginForm, RegistrationForm, UserEditForm, UserForm
from .token import account_activation_token
from .utils import send_user_email


@unauthenticated_user
def my_login_page(request):
    form = LoginForm()
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            now = timezone.now()
            try:
                _user = User.objects.get(email=email)
                login_attempt, created = LoginAttempt.objects.get_or_create(
                    user=_user
                )  # get the user's login attempt
                if (
                    login_attempt.timestamp
                    + timedelta(seconds=settings.LOGIN_ATTEMPTS_TIME_LIMIT)
                ) < now:
                    user = authenticate(request, username=email, password=password)
                    if user is not None:
                        login(request, user)
                        login_attempt.login_attempts = 0  # reset the login attempts
                        login_attempt.save()
                        return redirect(
                            "investicon:dashboard"
                        )  # change expected_url in your project
                    else:
                        # if the password is incorrect, increment the login attempts and
                        # if the login attempts == MAX_LOGIN_ATTEMPTS, set the user to be inactive and send activation email
                        login_attempt.login_attempts += 1
                        login_attempt.timestamp = now
                        login_attempt.save()
                        if login_attempt.login_attempts == settings.MAX_LOGIN_ATTEMPTS:
                            _user.is_active = False
                            _user.save()
                            # send the re-activation email
                            mail_subject = "Account suspended"
                            current_site = get_current_site(request)
                            send_user_email(
                                _user,
                                mail_subject,
                                email,
                                current_site,
                                "user/email_account_suspended.html",
                            )
                            messages.error(
                                request,
                                "Account suspended, maximum login attempts exceeded. "
                                "Reactivation link has been sent to your email",
                            )
                        else:
                            messages.error(request, "Incorrect email or password")
                            return redirect(settings.LOGIN_URL)
                else:
                    messages.error(request, "Login failed, please try again")
                    return redirect(settings.LOGIN_URL)

            except ObjectDoesNotExist:
                messages.error(request, "Try Incorrect email or password")
                return redirect(settings.LOGIN_URL)
        else:
            if form.errors:
                for field in form:
                    for error in field.errors:
                        messages.error(request, error)
    context = {"form": form}
    return render(request, "users/login.html", context)


@login_required
def logout_view(request):
    logout(request)
    return redirect("user:login")


@login_required
def user_update(request, pk):
    context = {}
    obj = get_object_or_404(User, id=pk)
    form = UserEditForm()
    if request.method == "POST":
        form = UserEditForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(
                request, "User Profile Information Has been Updated Successfully"
            )
            return redirect("investment:user-profiles")

    context["form"] = form
    return render(request, "user/create-profiles.html", context)


@login_required
def delete_user(request):
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        user.is_active = False
        user.save()
        delete_message = "Account will be rendered inactive for 3days before deleting. if you wish to recover account, Please contact the admin or use the reactivate account_link"
        messages.success(request, delete_message)
        return redirect("accounts:login")

    return render(request, "user/delete.html")


def activate_account_page(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.email_verified = True
        user.save()
        login_attempt, created = LoginAttempt.objects.get_or_create(user=user)
        if login_attempt.login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            login_attempt.login_attempts = 0
            login_attempt.save()
            messages.success(request, "Account restored, you can now proceed to login")
        else:
            messages.success(
                request,
                "Thank you for confirming your email. You can now proceed to Required Registration.",
            )
        return redirect("accounts:login")
    else:
        messages.error(
            request,
            "Thank you for confirming your email. You can now proceed to Required Registration.",
        )
        return redirect("accounts:login")


def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, "Your password was successfully updated!")
            return redirect("bank:dashboard")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "user/change_password.html", {"form": form})


def handler404(request, exception):
    return render(request, "user/404.html")


def handle_server_error(request):
    return render(request, "user/500.html")
