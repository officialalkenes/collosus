from django.urls import path

from . import views

app_name = "investicon"

urlpatterns = [
    # Home and Referrals
    path("", views.homepage, name="home"),
    path("referral/<str:ref_profile>/", views.homepage_ref, name="home"),
    # Dashboard Redirect
    path("dashboard/", views.dashboard, name="dashboard"),
    # Deposits and Records
    path("all-deposits/", views.admin_deposit_records, name="all-deposits"),
    path("create-deposit/", views.deposit_request, name="create-deposit"),
    path("deposit-records/", views.deposit_records, name="deposit-records"),
    path(
        "update-deposit/<str:slug>/", views.update_deposit_view, name="update-deposit"
    ),
    path(
        "admin-deposit-update/<str:slug>/",
        views.admin_update_deposit_view,
        name="admin-deposit-update",
    ),
    path(
        "admin-update-deposit/<int:pk>/",
        views.deposit_request,
        name="admin-update-deposit",
    ),
    # User Profiles
    path("user-profiles/", views.user_profile, name="user-profiles"),
    path("referred-users/", views.my_referrals, name="referred-users"),
    # Withdrawals and Records
    path(
        "admin-withdrawal-records/",
        views.admin_withdrawal_records,
        name="admin-withdrawal-records",
    ),
    path("create-withdrawal/", views.withdrawal_create, name="create-withdrawal"),
    path("withdrawal-records/", views.withdrawal_records, name="withdrawal-records"),
    path(
        "admin-withdrawal-update/<str:slug>/",
        views.admin_update_withdrawal_view,
        name="admin-withdrawal-update",
    ),
    # Investments and Records
    path(
        "admin-investment-update/<str:slug>/",
        views.admin_update_investment_view,
        name="admin-investment-update",
    ),
    path(
        "admin-investment-records/",
        views.admin_investment_records,
        name="admin-investment-records",
    ),
    path("investment-records/", views.investment_records, name="investment-records"),
    path("basic-invest/", views.create_basic_investment, name="basic-invest"),
    path("limited-invest/", views.create_limited_investment, name="limited-invest"),
    path(
        "unlimited-invest/", views.create_unlimited_investment, name="unlimited-invest"
    ),
    path("basic-invest/", views.create_basic_investment, name="basic-invest"),
    path("ira-invest/", views.ira_invest_now, name="ira-invest"),
]
