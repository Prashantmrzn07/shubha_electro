from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product
from .models import CartItem


@login_required
def cart_detail(request):
    items = CartItem.objects.filter(user=request.user).select_related("product", "product__brand")
    total = sum(item.line_total for item in items)
    return render(request, "cart/cart.html", {"items": items, "total": total})


@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except ValueError:
        quantity = 1
    if product.stock < 1:
        messages.error(request, "This product is currently out of stock.")
        return redirect(product.get_absolute_url())
    item, created = CartItem.objects.get_or_create(
        user=request.user, product=product, defaults={"quantity": 0}
    )
    item.quantity = min(product.stock, item.quantity + quantity)
    item.save()
    messages.success(request, f"{product.name} added to your cart.")
    return redirect("cart:detail")


@login_required
@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1
    if quantity < 1:
        item.delete()
        messages.info(request, "Item removed from cart.")
    else:
        item.quantity = min(item.product.stock, quantity)
        item.save()
        messages.success(request, "Cart updated.")
    return redirect("cart:detail")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect("cart:detail")
