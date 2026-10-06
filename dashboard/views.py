from datetime import datetime, timedelta
from decimal import Decimal
import csv

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from catalog.models import Brand, Category, Product, Review
from orders.models import Order
from .decorators import shop_admin_required
from .forms import (
    BrandForm,
    CategoryForm,
    DeliveryManageForm,
    OrderManageForm,
    PaymentManageForm,
    ProductForm,
)

User = get_user_model()


@shop_admin_required
def overview(request):
    today = timezone.localdate()
    paid_orders = Order.objects.exclude(status="cancelled").filter(payment__status="paid")
    daily_progress = []
    for days_ago in range(6, -1, -1):
        day = today - timedelta(days=days_ago)
        day_orders = Order.objects.filter(created_at__date=day)
        day_paid = paid_orders.filter(created_at__date=day)
        daily_progress.append(
            {
                "label": day.strftime("%a"),
                "date": day.strftime("%b %d"),
                "orders": day_orders.count(),
                "revenue": day_paid.aggregate(total=Sum("total"))["total"] or Decimal("0"),
            }
        )
    top_products = (
        Product.objects.filter(orderitem__order__status__in=["confirmed", "processing", "shipped", "delivered"])
        .annotate(units_sold=Sum("orderitem__quantity"))
        .order_by("-units_sold", "name")[:5]
    )
    context = {
        "product_count": Product.objects.count(),
        "active_product_count": Product.objects.filter(is_active=True).count(),
        "customer_count": User.objects.filter(role=User.ROLE_CUSTOMER).count(),
        "order_count": Order.objects.count(),
        "fulfilled_count": Order.objects.filter(status="delivered").count(),
        "revenue": paid_orders.aggregate(total=Sum("total"))["total"] or Decimal("0"),
        "today_orders": Order.objects.filter(created_at__date=today).count(),
        "low_stock": Product.objects.filter(stock__lte=settings.LOW_STOCK_THRESHOLD).order_by("stock")[:8],
        "recent_orders": Order.objects.select_related("user", "payment")[:8],
        "daily_progress": daily_progress,
        "top_products": top_products,
    }
    return render(request, "dashboard/overview.html", context)


@shop_admin_required
def category_list(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category saved.")
            return redirect("dashboard:categories")
    else:
        form = CategoryForm()
    return render(
        request,
        "dashboard/categories.html",
        {"form": form, "categories": Category.objects.annotate(product_count=Count("products"))},
    )


@shop_admin_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("dashboard:categories")
    else:
        form = CategoryForm(instance=category)
    return render(request, "dashboard/form.html", {"form": form, "title": "Edit category"})


@shop_admin_required
@require_POST
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.products.exists():
        messages.error(request, "Cannot delete a category that still has products.")
    else:
        category.delete()
        messages.success(request, "Category deleted.")
    return redirect("dashboard:categories")


@shop_admin_required
def brand_list(request):
    if request.method == "POST":
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand saved.")
            return redirect("dashboard:brands")
    else:
        form = BrandForm()
    return render(
        request,
        "dashboard/brands.html",
        {"form": form, "brands": Brand.objects.annotate(product_count=Count("products"))},
    )


@shop_admin_required
def brand_edit(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if request.method == "POST":
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand updated.")
            return redirect("dashboard:brands")
    else:
        form = BrandForm(instance=brand)
    return render(request, "dashboard/form.html", {"form": form, "title": "Edit brand"})


@shop_admin_required
@require_POST
def brand_delete(request, pk):
    brand = get_object_or_404(Brand, pk=pk)
    if brand.products.exists():
        messages.error(request, "Cannot delete a brand that still has products.")
    else:
        brand.delete()
        messages.success(request, "Brand deleted.")
    return redirect("dashboard:brands")


@shop_admin_required
def product_list(request):
    products = Product.objects.select_related("category", "brand")
    q = request.GET.get("q", "").strip()
    if q:
        products = products.filter(Q(name__icontains=q) | Q(brand__name__icontains=q))
    return render(
        request,
        "dashboard/products.html",
        {"products": products, "q": q, "low_stock_threshold": settings.LOW_STOCK_THRESHOLD},
    )


@shop_admin_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created.")
            return redirect("dashboard:products")
    else:
        form = ProductForm()
    return render(request, "dashboard/form.html", {"form": form, "title": "Add product"})


@shop_admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect("dashboard:products")
    else:
        form = ProductForm(instance=product)
    return render(request, "dashboard/form.html", {"form": form, "title": f"Edit {product.name}"})


@shop_admin_required
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect("dashboard:products")


@shop_admin_required
@require_POST
def inventory_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        stock = int(request.POST.get("stock", product.stock))
        if stock < 0:
            raise ValueError
    except ValueError:
        messages.error(request, "Stock must be a non-negative number.")
        return redirect("dashboard:products")
    product.stock = stock
    product.save(update_fields=["stock"])
    messages.success(request, f"Stock updated for {product.name}.")
    return redirect("dashboard:products")


@shop_admin_required
def customer_list(request):
    customers = User.objects.filter(role=User.ROLE_CUSTOMER).annotate(order_count=Count("orders"))
    return render(request, "dashboard/customers.html", {"customers": customers})


@shop_admin_required
def order_list(request):
    orders = Order.objects.select_related("user", "payment", "delivery")
    status = request.GET.get("status", "")
    if status:
        orders = orders.filter(status=status)
    return render(
        request,
        "dashboard/orders.html",
        {"orders": orders, "status": status, "statuses": Order.STATUS_CHOICES},
    )


@shop_admin_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("user", "payment", "delivery").prefetch_related("items"),
        pk=pk,
    )
    if request.method == "POST":
        order_form = OrderManageForm(request.POST, instance=order, prefix="order")
        payment_form = PaymentManageForm(request.POST, instance=order.payment, prefix="pay")
        delivery_form = DeliveryManageForm(request.POST, instance=order.delivery, prefix="ship")
        if order_form.is_valid() and payment_form.is_valid() and delivery_form.is_valid():
            order_form.save()
            payment_form.save()
            delivery_form.save()
            messages.success(request, "Order updated.")
            return redirect("dashboard:order_detail", pk=order.pk)
    else:
        order_form = OrderManageForm(instance=order, prefix="order")
        payment_form = PaymentManageForm(instance=order.payment, prefix="pay")
        delivery_form = DeliveryManageForm(instance=order.delivery, prefix="ship")
    return render(
        request,
        "dashboard/order_detail.html",
        {
            "order": order,
            "order_form": order_form,
            "payment_form": payment_form,
            "delivery_form": delivery_form,
        },
    )


@shop_admin_required
def review_list(request):
    reviews = Review.objects.select_related("product", "user")
    return render(request, "dashboard/reviews.html", {"reviews": reviews})


@shop_admin_required
@require_POST
def review_toggle(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_visible = not review.is_visible
    review.save(update_fields=["is_visible"])
    messages.success(request, "Review visibility updated.")
    return redirect("dashboard:reviews")


def _report_queryset(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    today = timezone.localdate()
    if not start:
        start = (today - timedelta(days=30)).isoformat()
    if not end:
        end = today.isoformat()
    start_date = datetime.fromisoformat(start).date()
    end_date = datetime.fromisoformat(end).date()
    orders = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    return orders, start, end


@shop_admin_required
def reports(request):
    orders, start, end = _report_queryset(request)
    paid = orders.filter(payment__status="paid").exclude(status="cancelled")
    summary = {
        "order_count": orders.count(),
        "paid_count": paid.count(),
        "cancelled": orders.filter(status="cancelled").count(),
        "revenue": paid.aggregate(total=Sum("total"))["total"] or Decimal("0"),
    }
    by_status = orders.values("status").annotate(count=Count("id"), total=Sum("total")).order_by("status")
    return render(
        request,
        "dashboard/reports.html",
        {
            "orders": orders.select_related("user", "payment")[:100],
            "summary": summary,
            "by_status": by_status,
            "start": start,
            "end": end,
        },
    )


@shop_admin_required
def reports_csv(request):
    orders, start, end = _report_queryset(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="sales-report-{start}-to-{end}.csv"'
    writer = csv.writer(response)
    writer.writerow(["Order ID", "Date", "Customer", "Status", "Payment", "Total"])
    for order in orders.select_related("user", "payment"):
        writer.writerow(
            [
                order.pk,
                timezone.localtime(order.created_at).strftime("%Y-%m-%d %H:%M"),
                order.user.get_username(),
                order.status,
                order.payment.status if hasattr(order, "payment") else "",
                order.total,
            ]
        )
    return response
