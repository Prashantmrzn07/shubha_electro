from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.overview, name="overview"),
    path("categories/", views.category_list, name="categories"),
    path("categories/<int:pk>/edit/", views.category_edit, name="category_edit"),
    path("categories/<int:pk>/delete/", views.category_delete, name="category_delete"),
    path("brands/", views.brand_list, name="brands"),
    path("brands/<int:pk>/edit/", views.brand_edit, name="brand_edit"),
    path("brands/<int:pk>/delete/", views.brand_delete, name="brand_delete"),
    path("products/", views.product_list, name="products"),
    path("products/new/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("products/<int:pk>/stock/", views.inventory_update, name="inventory_update"),
    path("customers/", views.customer_list, name="customers"),
    path("orders/", views.order_list, name="orders"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("reviews/", views.review_list, name="reviews"),
    path("reviews/<int:pk>/toggle/", views.review_toggle, name="review_toggle"),
    path("reports/", views.reports, name="reports"),
    path("reports/csv/", views.reports_csv, name="reports_csv"),
]
