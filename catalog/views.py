from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from orders.models import OrderItem
from .models import Brand, Category, Product, Review


def home(request):
    featured = Product.objects.filter(is_active=True).select_related("brand", "category")[:8]
    categories = Category.objects.all()
    return render(
        request,
        "catalog/home.html",
        {"featured": featured, "categories": categories},
    )


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("brand", "category")
    q = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    brand_slug = request.GET.get("brand", "")
    min_price = request.GET.get("min_price", "")
    max_price = request.GET.get("max_price", "")
    spec = request.GET.get("spec", "").strip()

    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(description__icontains=q)
            | Q(brand__name__icontains=q)
            | Q(specifications__icontains=q)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if spec:
        products = products.filter(specifications__icontains=spec)

    paginator = Paginator(products, 9)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "catalog/product_list.html",
        {
            "page": page,
            "categories": Category.objects.all(),
            "brands": Brand.objects.all(),
            "filters": {
                "q": q,
                "category": category_slug,
                "brand": brand_slug,
                "min_price": min_price,
                "max_price": max_price,
                "spec": spec,
            },
        },
    )


def _can_review(user, product):
    if not user.is_authenticated:
        return False
    if Review.objects.filter(user=user, product=product).exists():
        return False
    return OrderItem.objects.filter(
        order__user=user,
        product=product,
        order__status__in=["confirmed", "processing", "shipped", "delivered"],
    ).exists()


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("brand", "category"),
        slug=slug,
        is_active=True,
    )
    reviews = product.reviews.filter(is_visible=True).select_related("user")
    avg = reviews.aggregate(avg=Avg("rating"))["avg"]
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "avg_rating": avg,
            "can_review": _can_review(request.user, product),
        },
    )


@login_required
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if request.method != "POST":
        return redirect(product.get_absolute_url())
    if not _can_review(request.user, product):
        messages.error(request, "You can review a product after purchasing it.")
        return redirect(product.get_absolute_url())
    try:
        rating = int(request.POST.get("rating", 0))
    except ValueError:
        rating = 0
    comment = request.POST.get("comment", "").strip()
    if rating < 1 or rating > 5 or not comment:
        messages.error(request, "Please provide a rating (1-5) and a comment.")
        return redirect(product.get_absolute_url())
    Review.objects.create(product=product, user=request.user, rating=rating, comment=comment)
    messages.success(request, "Thank you for your review.")
    return redirect(product.get_absolute_url())
