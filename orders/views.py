from decimal import Decimal
import uuid

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import CartItem
from .models import Delivery, Order, OrderItem, Payment


@login_required
def order_list(request):
    orders = (
        Order.objects.filter(user=request.user)
        .select_related("payment", "delivery")
        .prefetch_related("items")
    )
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("payment", "delivery").prefetch_related("items"),
        pk=pk,
        user=request.user,
    )
    return render(request, "orders/order_detail.html", {"order": order})


@login_required
def checkout(request):
    items = list(
        CartItem.objects.filter(user=request.user).select_related("product")
    )
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("cart:detail")

    for item in items:
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f"Not enough stock for {item.product.name}. Please update your cart.",
            )
            return redirect("cart:detail")

    total = sum(item.line_total for item in items)
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "Kathmandu").strip() or "Kathmandu"
        notes = request.POST.get("notes", "").strip()
        method = request.POST.get("payment_method", "cod")
        mock_result = request.POST.get("mock_result", "paid")
        if not full_name or not phone or not address:
            messages.error(request, "Delivery name, phone and address are required.")
            return render(
                request,
                "orders/checkout.html",
                {"items": items, "total": total, "user": request.user},
            )
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    total=Decimal(total),
                    notes=notes,
                    status="pending",
                )
                for item in items:
                    product = item.product
                    product.refresh_from_db()
                    if item.quantity > product.stock:
                        raise ValueError(f"Not enough stock for {product.name}.")
                    product.stock -= item.quantity
                    product.save(update_fields=["stock"])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=item.quantity,
                    )
                if method == "mock_card":
                    pay_status = "paid" if mock_result == "paid" else "failed"
                    reference = uuid.uuid4().hex[:12].upper()
                else:
                    pay_status = "unpaid"
                    reference = "COD"
                Payment.objects.create(
                    order=order,
                    method=method if method in {"mock_card", "cod"} else "cod",
                    status=pay_status,
                    amount=order.total,
                    reference=reference,
                )
                Delivery.objects.create(
                    order=order,
                    full_name=full_name,
                    phone=phone,
                    address=address,
                    city=city,
                    notes=notes,
                )
                if pay_status == "failed":
                    order.status = "cancelled"
                    order.save(update_fields=["status"])
                    for item in items:
                        item.product.stock += item.quantity
                        item.product.save(update_fields=["stock"])
                else:
                    order.status = "confirmed"
                    order.save(update_fields=["status"])
                    CartItem.objects.filter(user=request.user).delete()
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("cart:detail")

        if pay_status == "failed":
            messages.error(request, "Mock payment failed. No order was confirmed.")
            return redirect("cart:detail")
        messages.success(request, f"Order #{order.pk} placed successfully.")
        return redirect("orders:detail", pk=order.pk)

    return render(
        request,
        "orders/checkout.html",
        {"items": items, "total": total},
    )
