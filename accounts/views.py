from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import AdminLoginForm, LoginForm, ProfileForm, RegisterForm


class CustomerLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        user = self.request.user
        if getattr(user, "is_shop_admin", False):
            return "/dashboard/"
        return super().get_success_url()


class AdminLoginView(LoginView):
    template_name = "accounts/admin_login.html"
    authentication_form = AdminLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return "/dashboard/"


class CustomerLogoutView(LogoutView):
    http_method_names = ["get", "post"]


def register(request):
    if request.user.is_authenticated:
        return redirect("catalog:home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect("catalog:home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})
@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})
