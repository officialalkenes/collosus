from django.urls import path

from . import views

app_name = "investicon"

urlpatterns = [
    path("", views.homepage, name="home"),
    path("referral/<str:ref_profile>/", views.homepage_ref, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("deposit-records/", views.deposit_records, name="deposit-records"),
    path("all-deposits/", views.admin_deposit_records, name="all-deposits"),
    path(
        "admin-withdrawal-records/",
        views.admin_widthrawal_records,
        name="admin-withdrawal-records",
    ),
    path(
        "admin-deposit-update/<pk>/",
        views.admin_update_deposit_view,
        name="admin-deposit-update",
    ),
    path("user-profiles/", views.user_profile, name="user-profiles"),
    path("withdrawal-records/", views.withdrawal_records, name="withdrawal-records"),
    path("investment-records/", views.investment_records, name="investment-records"),
    path("create-deposit/", views.deposit_request, name="create-deposit"),
    path(
        "admin-update-deposit/<int:pk>/",
        views.deposit_request,
        name="admin-update-deposit",
    ),
    path("create-withdrawal/", views.withdrawal_create, name="create-withdrawal"),
    path("basic-invest/", views.create_basic_investment, name="basic-invest"),
    path("limited-invest/", views.limited_invest_now, name="limited-invest"),
    path("unlimited-invest/", views.unlimited_invest_now, name="unlimited-invest"),
    path("basic-invest/", views.create_basic_investment, name="basic-invest"),
    path("basic-invest/", views.create_basic_investment, name="basic-invest"),
    path("referred-users/", views.my_referrals, name="referred-users"),
]
