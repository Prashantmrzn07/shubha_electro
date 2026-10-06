import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from catalog.models import Product

c = Client()
print("anon")
for p in [
    reverse("catalog:home"),
    reverse("catalog:product_list"),
    reverse("accounts:login"),
    reverse("accounts:register"),
]:
    r = c.get(p)
    print(p, r.status_code)
    if r.status_code >= 400:
        raise SystemExit(f"failed {p}")

User = get_user_model()
assert c.login(username="prashant", password="prashant123")
product = Product.objects.first()
print("customer")
for path in [
    reverse("catalog:product_detail", args=[product.slug]),
    reverse("cart:detail"),
    reverse("orders:list"),
    reverse("orders:checkout"),
    reverse("accounts:profile"),
]:
    r = c.get(path)
    print(path, r.status_code)
    if r.status_code >= 400:
        raise SystemExit(f"failed {path}")

c.logout()
admin_logged_in = c.login(username="admin", password="admin123") or c.login(
    username="prashantmhrh77@gail.com", password="Prashant6969"
)
assert admin_logged_in, "Failed to login as admin"
print("admin")
for name in ["overview", "products", "categories", "brands", "customers", "orders", "reviews", "reports"]:
    path = reverse(f"dashboard:{name}")
    r = c.get(path)
    print(path, r.status_code)
    if r.status_code >= 400:
        raise SystemExit(f"failed {path}")
csv = c.get(reverse("dashboard:reports_csv"))
print("csv", csv.status_code, csv["Content-Type"])
print("ok")
