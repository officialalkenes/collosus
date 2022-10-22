from datetime import datetime, timedelta

from django.conf import settings
from django.core.management import BaseCommand

from investment.models import Investment

User = settings.AUTH_USER_MODEL


class Command(BaseCommand):
    help = "Delete Invalid Users for 3 days"

    def handle(self, *args, **kwargs):
        users = User.objects.filter(is_active=False)
        today = datetime.today
        for user in users:
            if user.start_date + timedelta(days=3) > today:
                user.delete()
                self.stdout.write(f"User {user.username} deleted successfully!")
