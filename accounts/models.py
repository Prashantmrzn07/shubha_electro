from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CUSTOMER = "customer"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_ADMIN, "Administrator"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.role == self.ROLE_ADMIN:
            self.is_staff = True
        super().save(*args, **kwargs)

    @property
    def is_shop_admin(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def display_name(self):
        full = self.get_full_name().strip()
        if full:
            return full
        if self.first_name:
            return self.first_name
        if self.email and "@" in self.email:
            return self.email.split("@")[0]
        return self.username

    @property
    def avatar_initial(self):
        if self.first_name:
            return self.first_name[0].upper()
        if self.username:
            return self.username[0].upper()
        if self.email:
            return self.email[0].upper()
        return "U"
