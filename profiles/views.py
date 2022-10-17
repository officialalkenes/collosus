from django.shortcuts import render


def update_user_profiles(request):
    context = {}
    return render(request, "profiles/profile-update.html", context)
