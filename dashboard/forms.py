from django import forms

from catalog.models import Brand, Category, Product
from orders.models import Delivery, Order, Payment


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "name",
            "description",
            "specifications",
            "warranty",
            "price",
            "stock",
            "is_active",
            "image",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "specifications": forms.Textarea(attrs={"rows": 5}),
            "image": forms.ClearableFileInput(
                attrs={
                    "accept": "image/jpeg,image/png,image/webp,image/gif",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "input"
        self.fields["image"].label = "Product image"
        self.fields["image"].help_text = "Upload JPG, PNG, WEBP or GIF. Recommended: clear product image on a light background."


class OrderManageForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"


class PaymentManageForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"


class DeliveryManageForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ["status", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"
