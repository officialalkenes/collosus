from django.contrib import admin

# Register your models here.
from .models import Profile
from users.models import UserActivity, LoginAttempt


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "occupation", "balance", "count"]


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ["login", "logout"]


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ["user", "login_attempts", "timestamp"]
    search_fields = ["user"]
