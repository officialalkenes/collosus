from datetime import datetime

from django.db.models import Sum

from django.contrib.sites.shortcuts import get_current_site
from investment.models import Investment


from profiles.models import Profile


def items(request):
    now = datetime.now()
    current_site = get_current_site(request)
    user = None
    profile = None
    investments = None

    try:
        # user = request.user
        # profile = Profile.objects.filter(user=request.user)
        investments = Investment.objects.filter(user=user, status="Successful")
        amount = investments.aggregate(sum=Sum("amount"))["sum"] or 0
        if len(investments) < 1:
            total = 0
        else:
            total = len(investments)
    except Profile.DoesNotExist or Profile.MultipleObjectsReturned:
        user = None
        profile = None
        # prof_length = ""
    return {
        "now": now,
        "current_site": current_site,
        "profile": profile,
        "total": total,
        "amount": amount,
        # 'prof_length': prof_length,
    }
