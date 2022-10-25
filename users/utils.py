from smtplib import SMTPException
from socket import gaierror

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .token import account_activation_token


def send_user_email(user, mail_subject, to_email, current_site, template):
    message = render_to_string(
        template,
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.id)),
            "token": account_activation_token.make_token(user),
        },
    )
    try:
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
        return "success"
    except (ConnectionAbortedError, SMTPException, gaierror):
        return "error"


def send_investment_update(
    user,
    mail_subject,
    amount,
    email,
    profit,
    total,
    template,  # end_date
):
    message = render_to_string(
        template,
        {
            "user": user,
            "amount": amount,
            "profit": profit,
            "total": float(total),
            # "end_date": end_date,
        },
    )
    try:
        send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, [email])
        return "success"
    except (ConnectionAbortedError, SMTPException, gaierror):
        return "error"
