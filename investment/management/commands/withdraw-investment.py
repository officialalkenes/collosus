from django.core.management import BaseCommand

from django.contrib.auth import get_user_model

from django.contrib.sites.shortcuts import get_current_site

from investment.models import Investment
from profiles.models import Profile

from users.utils import send_investment_update

User = get_user_model()

current_site = get_current_site()

users = User.objects.filter(is_active=True)


class Command(BaseCommand):
    help = "Withdraw Investments for completed investments"

    def handle(self, *args, **kwargs):
        if users:
            for user in users:
                try:
                    investments = Investment.objects.filter(
                        user=user, status="Successful", completed=True
                    )
                    profile = Profile.objects.filter(user=user)
                    for investment in investments:
                        balance = investment.profit
                        profile.balance += balance
                        profile.save()
                        mail_subject = "Successful Withdrawal Update"
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
                except Investment.DoesNotExist:
                    pass
