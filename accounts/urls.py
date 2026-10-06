from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.CustomerLoginView.as_view(), name="login"),
    path("admin-login/", views.AdminLoginView.as_view(), name="admin_login"),
    path("logout/", views.CustomerLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
]
