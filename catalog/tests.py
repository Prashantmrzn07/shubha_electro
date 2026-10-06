from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from catalog.models import Brand, Category, Product
from cart.models import CartItem
from orders.models import Order

User = get_user_model()


class ShopFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Televisions")
        self.brand = Brand.objects.create(name="Samsung")
        self.product = Product.objects.create(
            category=self.category,
            brand=self.brand,
            name="Test TV",
            description="A test television",
            specifications="Screen: 43 inch",
            warranty="1 year",
            price="10000.00",
            stock=5,
        )
        self.customer = User.objects.create_user(
            username="buyer",
            password="pass12345",
            role=User.ROLE_CUSTOMER,
        )
        self.admin = User.objects.create_user(
            username="shopadmin",
            password="pass12345",
            role=User.ROLE_ADMIN,
            is_staff=True,
        )

    def test_home_and_catalog(self):
        home = self.client.get(reverse("catalog:home"))
        self.assertEqual(home.status_code, 200)
        listing = self.client.get(reverse("catalog:product_list"), {"q": "TV", "category": "televisions"})
        self.assertEqual(listing.status_code, 200)
        self.assertContains(listing, "Test TV")
        detail = self.client.get(self.product.get_absolute_url())
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, "1 year")

    def test_register_cart_checkout_and_track(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "first_name": "New",
                "last_name": "User",
                "email": "new@example.com",
                "password1": "StrongPass!234",
                "password2": "StrongPass!234",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.client.post(reverse("cart:add", args=[self.product.pk]), {"quantity": 1})
        self.assertEqual(CartItem.objects.count(), 1)
        checkout = self.client.post(
            reverse("orders:checkout"),
            {
                "full_name": "New User",
                "phone": "9801111111",
                "address": "Kathmandu",
                "city": "Kathmandu",
                "payment_method": "mock_card",
                "mock_result": "paid",
            },
        )
        self.assertEqual(checkout.status_code, 302)
        order = Order.objects.get()
        self.assertEqual(order.status, "confirmed")
        self.assertEqual(order.payment.status, "paid")
        track = self.client.get(reverse("orders:detail", args=[order.pk]))
        self.assertEqual(track.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)

    def test_admin_dashboard(self):
        self.client.login(username="shopadmin", password="pass12345")
        overview = self.client.get(reverse("dashboard:overview"))
        self.assertEqual(overview.status_code, 200)
        reports = self.client.get(reverse("dashboard:reports"))
        self.assertEqual(reports.status_code, 200)
        forbidden = self.client
        self.client.logout()
        self.client.login(username="buyer", password="pass12345")
        blocked = self.client.get(reverse("dashboard:overview"))
        self.assertEqual(blocked.status_code, 403)
