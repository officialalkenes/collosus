from django.conf import settings
from django.core.management import BaseCommand

from django.contrib.sites.shortcuts import get_current_site

from investment.models import Investment
from users.utils import send_investment_update

User = settings.AUTH_USER_MODEL

users = User.objects.filter(is_active=True)

current_site = get_current_site()


class Command(BaseCommand):
    help = "Delete Invalid Users for 3 days"

    def handle(self, *args, **kwargs):
        for user in users:
            investment = Investment.objects.filter(
                user=user, status="Successful", completed=False
            )
            percentage = investment.percentage * investment.amount
            investment.profit += percentage
            investment.save()
            mail_subject = "Investment Update"
            amount = investment.amount
            profit = investment.profit
            email = user.email
            total = amount + profit
            end_date = investment.end_date
            self.stdout.write(
                f"User {user.username}'s Investment Updated successfully!"
            )

            send_investment_update(
                user,
                mail_subject,
                amount,
                email,
                profit,
                total,
                end_date,
                current_site,
                "users/email_investment_update.html",
            )
