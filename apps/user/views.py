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
