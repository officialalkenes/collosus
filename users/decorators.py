from django.shortcuts import redirect
from django.urls import reverse


# when the user is authenticated, we redirect them to the Dashboard page.
def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(
                reverse("investment:dashboard")
            )  # Change the redirect url in your project
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


# remember also to change the redirect url in tests/test_views.py lines 22 and 104
