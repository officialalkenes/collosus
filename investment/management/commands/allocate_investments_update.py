from django.conf import settings
from django.core.management import BaseCommand

from django.contrib.auth import get_user_model

from django.contrib.sites.shortcuts import get_current_site

from investment.models import Investment
from users.utils import send_investment_update

User = get_user_model()

users = User.objects.filter(is_active=True)


class Command(BaseCommand):
    help = "Allocate Investment Profits Daily for active investments"

    def handle(self, *args, **kwargs):
        if users:
            for user in users:
                try:
                    investments = Investment.objects.filter(
                        user=user, status="Successful", completed=False
                    )
                    for investment in investments:
                        percentage = investment.percentage * investment.amount
                        investment.profit += percentage
                        investment.save()
                        mail_subject = "Investment Update"
                        amount = investment.amount
                        profit = investment.profit
                        email = user.email
                        total = amount + profit
                        end_date = investment.end_date.strftime("%a %m %y")
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
                            "users/email_investment_update.html",
                        )
                    else:
                        self.stdout.write("No Investment Updated Available")

                except Investment.DoesNotExist:
                    pass
