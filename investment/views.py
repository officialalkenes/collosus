from datetime import datetime, date
from http.client import HTTPResponse
from xml.dom import ValidationErr
from django.contrib.messages.views import SuccessMessageMixin

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site


from django.db.models import Sum
from django.db.transaction import atomic

from django.shortcuts import redirect, render, get_object_or_404

from django.urls import reverse

from django.views.generic import CreateView, FormView, UpdateView

# Create your views here.
from django.contrib.auth import get_user_model
from investment.forms import (
    BasicInvestmentForm,
    DepositForm,
    DepositProofForm,
    LimitedInvestmentForm,
    TransferInvestmentForm,
    UnlimitedInvestmentForm,
    IraInvestmentForm,
    UpdateDepositForm,
)
from users.utils import send_withdrawal_update

from .mixins import AdminRequiredMixin

from investment.models import (
    Deposit,
    Investment,
    Portfolio,
    Withdrawal,
)
from profiles.models import Profile

User = get_user_model()


def homepage_ref(request, *args, **kwargs):
    code = str(kwargs.get("ref_profile"))
    try:
        profile = Profile.objects.get(code=code)
        print("profile")
        request.session["ref_profile"] = str(profile.pkid)
    except ValidationErr:
        pass

    print(request.session.get_expiry_age())

    # form = ContactForm()
    # if request.method == 'POST':
    #     form = ContactForm(request.POST)
    #     if form.is_valid():
    #         name = form.cleaned_data.get('name')
    #         email = form.cleaned_data.get('email')
    #         subject = form.cleaned_data.get('subject')
    #         message = form.cleaned_data.get('message')
    return render(request, "investicon/homepage.html")


def homepage(request):
    return render(request, "investicon/homepage.html")


@login_required
def dashboard(request):
    try:
        user = request.user
        profiling = Profile.objects.filter(user=user)
        deposits = Deposit.objects.filter(user=user)
        withdrawal = Withdrawal.objects.filter(user=user)
        investments = Investment.objects.filter(
            user=user, status="Successful", completed=False
        )
        amount = investments.aggregate(sum=Sum("amount"))["sum"] or 0
        profits = investments.aggregate(sum=Sum("profit"))["sum"] or 0
        net_total = profits + amount
        if len(investments) < 1:
            total = 0
        else:
            total = len(investments)

    except Profile.MultipleObjectsReturned or Deposit.MultipleObjectsReturned or Withdrawal.MultipleObjectsReturned:
        pass
    context = {
        "profiling": profiling,
        "deposits": deposits,
        "withdrawal": withdrawal,
        "total": total,
        "net_total": net_total,
    }
    return render(request, "investicon/index.html", context)


class CreateDeposit(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Deposit
    fields = [
        "amount",
        "payment",
    ]
    template_name = "investicon/deposit.html"
    success_message = "Deposit has been created successfully!"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("investicon:deposit-records")


deposit_request = CreateDeposit.as_view()


class UpdateDeposit(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Deposit
    fields = ("amount", "payment", "status")
    template_name = "investicon/admin-deposit.html"
    success_message = "Your Deposit request has been updated successfully!"

    def form_valid(self, form):
        user = form.instance.user
        amount = form.instance.amount
        profile = Profile.objects.filter(user=user).first()
        if form.instance.status == "Successful":
            profile.balance += amount
            profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("investicon:deposit-records")


admin_update_deposit_view = UpdateDeposit.as_view()


class UpdateInvestment(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Investment
    fields = ("amount", "profit", "completed", "status", "start_date", "end_date")

    template_name = "investicon/admin-investment.html"
    success_message = "Your Withrawal request has been updated successfully!"

    def form_valid(self, form):
        user = form.instance.user
        amount = form.instance.amount
        profile = Profile.objects.filter(user=user).first()
        if form.instance.completed is True:
            profit = form.instance.profit
            profile.balance += amount
            profile.balance += profit
            profile.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("investicon:investment-records")


admin_update_investment_view = UpdateInvestment.as_view()


# @login_required
# def withdraw_investment(request):
#     investments = Investment.objects.filter(
#         user=request.user,
#         completed=True,
#     )


class UpdateWithdrawal(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Withdrawal
    fields = ("amount", "address", "status")
    template_name = "investicon/admin-withdrawal.html"
    success_message = "Your Withrawal request has been updated successfully!"

    def form_valid(self, form):
        user = form.instance.user
        email = user.email
        amount = form.instance.amount
        profile = Profile.objects.get(user=user)
        balance = profile.balance
        if form.instance.status == "Successful" and balance >= amount:
            profile.balance -= amount
            balance = profile.balance
            profile.save()
            subject = "Withdrawal Update"
            send_withdrawal_update(
                user,
                subject,
                amount,
                email,
                balance,
                "users/email_withdrawal_update.html",
            )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("investicon:admin-withdrawal-records")


admin_update_withdrawal_view = UpdateWithdrawal.as_view()


# Deposit Proof
@login_required
def update_deposit_view(request, slug):
    context = {}
    obj = get_object_or_404(Deposit, slug=slug)
    # pass the object as instance in form
    form = DepositProofForm(request.POST or None, request.FILES or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, "Your Deposit proof has been updated successfully")
        return redirect("banks:user-profiles")

    # add form dictionary to context
    context["form"] = form
    return render(request, "investicon/update-deposit.html", context)


class CreateWithdrawal(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Withdrawal
    fields = ("amount",)
    template_name = "investicon/withdrawal.html"
    success_message = "Your Withrawal request is Currently being processed!"

    def form_valid(self, form):
        user = self.request.user
        profile = Profile.objects.filter(user=user).first()
        amount = form.instance.amount
        if profile.balance >= amount:
            form.instance.user = user
            form.instance.address = profile.btc_wallet
            form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("investicon:withdrawal-records")


withdrawal_create = CreateWithdrawal.as_view()


# class CreateBasicInvestment(LoginRequiredMixin, SuccessMessageMixin, CreateView):
#     model = Investment
#     fields = ("amount",)
#     template_name = "investicon/basic-investment.html"
#     success_message = "You have successfully subscribed to basic investment!"

#     def form_valid(self, form):
#         user = self.request.user
#         amount = form.instance.amount
#         form.instance.status = "Successful"
#         form.instance.user = user
#         profile = Profile.objects.filter(user=user).first()
#         if form.instance.status == "Successful" and amount <= profile.balance:
#             profile.balance -= amount
#             profile.save()
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse("investicon:withdrawal-records")


# create_basic_investment = CreateBasicInvestment.as_view()
@login_required
def create_basic_investment(request):
    form = BasicInvestmentForm()
    user = request.user
    if request.method == "POST":
        form = BasicInvestmentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get("amount")
            profile = Profile.objects.get(user=user)
            if profile.balance >= amount:
                Investment.objects.create(
                    user=user,
                    amount=float(amount),
                    status="Successful",
                    investment_type="Basic",
                )
                profile.balance -= amount
                profile.save()
                messages.success(
                    request,
                    "You Have Successfully Subscribe to the basic investment plan",
                )
                return redirect("investicon:investment-records")
            else:
                messages.error(
                    request, "Your account balance is lower than your deposit plan"
                )
                return redirect("investicon:basic-invest")
    context = {"form": form}
    return render(request, "investicon/basic-investment.html", context)


@login_required
def create_limited_investment(request):
    form = LimitedInvestmentForm()
    user = request.user
    if request.method == "POST":
        form = LimitedInvestmentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get("amount")
            profile = Profile.objects.get(user=user)
            if profile.balance >= amount:
                Investment.objects.create(
                    user=user,
                    amount=float(amount),
                    status="Successful",
                    investment_type="Limited",
                )
                profile.balance -= amount
                profile.save()
                messages.success(
                    request,
                    "You Have Successfully Subscribe to the Limited Investment plan",
                )
                return redirect("investicon:investment-records")
            else:
                messages.error(
                    request, "Your account balance is lower than your Investment plan"
                )
                return redirect("investicon:limited-invest")
    context = {"form": form}
    return render(request, "investicon/basic-investment.html", context)


@login_required
def create_ira_investment(request):
    form = IraInvestmentForm()
    user = request.user
    if request.method == "POST":
        form = IraInvestmentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get("amount")
            profile = Profile.objects.get(user=user)
            if profile.balance >= amount:
                Investment.objects.create(
                    user=user,
                    amount=float(amount),
                    status="Successful",
                    investment_type="Ira",
                )
                profile.balance -= amount
                profile.save()
                messages.success(
                    request,
                    "You Have Successfully Subscribe to the Ira investment plan",
                )
                return redirect("investicon:investment-records")
            else:
                messages.error(
                    request, "Your account balance is lower than your Investment plan"
                )
                return redirect("investicon:limited-invest")
    context = {"form": form}
    return render(request, "investicon/ira-investment.html", context)


@login_required
def create_unlimited_investment(request):
    form = UnlimitedInvestmentForm()
    user = request.user
    if request.method == "POST":
        form = UnlimitedInvestmentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data.get("amount")
            profile = Profile.objects.get(user=user)
            if profile.balance >= amount:
                Investment.objects.create(
                    user=user,
                    amount=float(amount),
                    status="Successful",
                    investment_type="Basic",
                )
                profile.balance -= amount
                profile.save()
                messages.success(
                    request,
                    "You Have Successfully Subscribe to the Unlimited investment plan",
                )
                return redirect("investicon:investment-records")
            else:
                messages.error(
                    request, "Your account balance is lower than your deposit plan"
                )
                return redirect("investicon:unlimited-invest")
    context = {"form": form}
    return render(request, "investicon/unlimited-investment.html", context)


def update_investment(request, pk):
    obj = get_object_or_404(Investment, pk)
    form = TransferInvestmentForm()
    if request.method == "POST":
        form = TransferInvestmentForm(request.POST or None, instance=obj)
        if form.is_valid():
            user = form.cleaned_data.get("user")
            profile = Profile.objects.get(user=user)
            profit = form.cleaned_data.get("profit")
            amount = form.instance.amount
            profile.amount += profit
            form.save()
        else:
            remainder = amount - profile.balance
            form.delete()
            messages.error(f"You need {remainder} to invest in this plan")
            return redirect("investment:deposit")
    context = {"form": form}
    return render(request, "investicon/limited-investment.html", context)


# Forms

# @login_required
# def basic_invest_now(request):
#     form = BasicInvestmentForm()
#     if request.method == "POST":
#         form = BasicInvestmentForm(request.POST, request.user)
#         if form.is_valid():
#             amount = form.cleaned_data.get('amount')
#             form.investment_type = "Basic"
#             form.save()
#             message = f"You have invest {amount} from your deposit. Happy Investing"
#             messages.success(request, message)
#             return redirect('investment:investment-records')
#     context = {
#         'form': form
#     }
#     return render(request, 'investicon/basic-investment.html', context)


@login_required
def limited_invest_now(request):
    form = LimitedInvestmentForm()
    if request.method == "POST":
        investment_type = Investment.objects.get(investment_type="Limited")
        form = LimitedInvestmentForm(
            request.POST, user=request.user, investment_type=investment_type
        )
        if form.is_valid():
            amount = form.cleaned_data.get("amount")
            amount = amount * 1.00
            profile = Profile.objects.filter(user=request.user)
            if amount <= profile.balance:
                profile.balance -= amount
                profile.save()
                form.save()
                message = f"You have invest {amount} from your deposit. Please wait for our agents to verify your investment. Happy Investing"
                messages.success(request, message)
                return redirect("investicon:investment-records")
            else:
                remainder = amount - profile.balance
                form.delete()
                messages.error(f"You need {remainder} to invest in this plan")
                return redirect("investment:deposit")
    context = {"form": form}
    return render(request, "investicon/limited-investment.html", context)


@login_required
def unlimited_invest_now(request):
    form = UnlimitedInvestmentForm()
    if request.method == "POST":
        investment_type = Investment.objects.get(investment_type="Limited")
        form = UnlimitedInvestmentForm(
            request.POST, user=request.user, investment_type=investment_type
        )
        if form.is_valid():
            amount = form.cleaned_data.get("amount")
            amount = amount * 1.00
            profile = Profile.objects.filter(user=request.user)
            if amount <= profile.balance:
                profile.balance -= amount
                profile.save()
                form.save()
                message = f"You have invest {amount} from your deposit. Please wait for our agents to verify your investment. Happy Investing"
                messages.success(request, message)
                return redirect("investment:investment-records")
            else:
                remainder = amount - profile.balance
                form.delete()
                messages.error(f"You need {remainder} to invest in this plan")
                return redirect("investment:deposit")
    context = {"form": form}
    return render(request, "investicon/create-investment.html", context)


@login_required
def ira_invest_now(request):
    form = IraInvestmentForm()
    if request.method == "POST":
        investment_type = Investment.objects.get(investment_type="Limited")
        form = IraInvestmentForm(
            request.POST, user=request.user, investment_type=investment_type
        )
        if form.is_valid():
            amount = form.cleaned_data.get("amount")
            amount = amount * 1.00
            profile = Profile.objects.filter(user=request.user)
            if amount <= profile.balance:
                profile.balance -= amount
                profile.save()
                form.save()
                message = f"You have invest {amount} from your deposit. Please wait for our agents to verify your investment. Happy Investing"
                messages.success(request, message)
                return redirect("investment:investment-records")
            else:
                remainder = amount - profile.balance
                form.delete()
                messages.error(f"You need {remainder} to invest in this plan")
                return redirect("investment:deposit")
    context = {"form": form}
    return render(request, "investicon/ira-investment.html", context)


# Records
@login_required
def admin_investment_records(request):
    records = Investment.objects.all()
    context = {"records": records}
    return render(request, "investicon/all-investment-records.html", context)


@login_required
def investment_records(request):
    records = Investment.objects.filter(user=request.user)
    context = {
        "records": records,
    }
    return render(request, "investicon/investment-records.html", context)


@login_required
def deposit_records(request):
    deposit_records = Deposit.objects.filter(user=request.user)
    context = {
        "deposits": deposit_records,
    }
    return render(request, "investicon/deposit-records.html", context)


@login_required
def withdrawal_records(request):
    withdrawal = Withdrawal.objects.filter(user=request.user)
    context = {
        "withdrawal": withdrawal,
    }
    return render(request, "investicon/withdrawal-records.html", context)


@login_required
def admin_deposit_records(request):
    deposit_records = Deposit.objects.all()
    context = {
        "deposits": deposit_records,
    }
    return render(request, "investicon/all-deposit-records.html", context)


@login_required
def admin_withdrawal_records(request):
    withdrawal_records = Withdrawal.objects.all()
    context = {
        "withdrawal": withdrawal_records,
    }
    return render(request, "investicon/all-withdrawal-records.html", context)


@login_required
def user_profile(request):
    user = request.user
    try:
        profiler = Profile.objects.filter(user=user)
    except ValidationErr:
        pass
    context = {
        "profiler": profiler,
    }
    return render(request, "investicon/user_details.html", context)


@login_required
def my_referrals(request):
    profile = Profile.objects.get(user=request.user)
    total_ref = profile.get_recommended_profiles()
    context = {
        "total_ref": total_ref,
    }
    return render(request, "investicon/referral-table.html", context)


class UpdateInvestment(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Deposit
    fields = ("amount", "payment", "status")
    template_name = "investicon/deposit.html"
    success_message = "Your Deposit request has been updated successfully!"


@login_required
def withdraw_investment_request(request, pk):
    today = date.today()
    try:
        investment = Investment.objects.get(id=pk)
        user = request.user
    except Investment.MultipleObjectsReturned or Investment.DoesNotExist:
        investment = None
    if investment is not None:
        if investment.end_date >= today and investment.status == "Successful":
            profile = user.profile
            profile_balance = profile.balance
            total_withdraw = investment.profit + investment.amount
            profile_balance += total_withdraw
            profile.save()
            messages.success(
                "Your Investment has been withdrawn to your balance successfully"
            )
            return redirect("investment:investment-records")
        else:
            messages.error("You can't withdraw investment yet")
            return redirect("investment:investment-records")
    context = {"investment": investment}
    return render(request, "", context)


# class UpdateWithdrawal(LoginRequiredMixin, UpdateView):
#     model = Withdrawal
#     fields = ("amount", "payment", "status")
#     template_name = "investicon/withdrawal.html"
#     success_message = "Your Withrawal request has been updated successfully!"

#     def form_valid(self, form):
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse("investment:withdrawal-records")


# withdrawal_create = CreateWithdrawal.as_view()
