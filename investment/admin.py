from django.contrib import admin

from investment.models import Deposit, Investment, Withdrawal

# Register your models here.


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ["amount", "user", "payment", "wallet_address", "status", "trx"]
    list_display_links = [
        "amount",
        "user",
        "payment",
        "status",
    ]


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ["amount", "user", "address", "status", "trx"]
    list_display_links = [
        "amount",
        "user",
        "address",
        "status",
    ]


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ["amount", "user", "profit", "total_percentage"]
    list_display_links = [
        "amount",
        "user",
        "profit",
        "total_percentage",
    ]
