from datetime import datetime

from django.contrib.sites.shortcuts import get_current_site
from investment.models import Investment


from profiles.models import Profile


def items(request):
    now = datetime.now()
    current_site = get_current_site(request)

    try:
        # user = request.user
        profile = Profile.objects.filter()
        # investments = Investment.objects.filter(user=user, status="Successful")
        # total = len(investments)
    except Profile.DoesNotExist or Profile.MultipleObjectsReturned:
        # user = None
        profile = None
    return {
        "now": now,
        "current_site": current_site,
        "profile": profile,
        # "total": total,
    }
