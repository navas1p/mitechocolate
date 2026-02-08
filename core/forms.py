from django import forms
from django.forms import inlineformset_factory

from . import models


class AdminAssistantForm(forms.Form):
    question = forms.CharField(
        label="Business question",
        widget=forms.Textarea(attrs={"rows": 6, "placeholder": "Ask about the business rules..."}),
    )


class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["base_unit"].required = True

    class Meta:
        model = models.Product
        fields = [
            "name",
            "name_arabic",
            "product_type",
            "barcode",
            "base_unit",
            "taxes",
            "unit_price",
            "max_discount_amount",
        ]


class ProductUnitPriceForm(forms.ModelForm):
    class Meta:
        model = models.ProductUnitPrice
        fields = ["unit", "conversion_factor", "sales_price"]


ProductUnitPriceFormSet = inlineformset_factory(
    models.Product,
    models.ProductUnitPrice,
    form=ProductUnitPriceForm,
    extra=1,
    can_delete=True,
)


class ProductionForm(forms.ModelForm):
    class Meta:
        model = models.Production
        fields = [
            "product",
            "unit",
            "quantity",
            "batch_number",
            "production_date",
            "expiry_date",
        ]
        widgets = {
            "production_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = models.Purchase
        fields = ["date", "supplier", "invoice_number", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class PurchaseItemForm(forms.ModelForm):
    class Meta:
        model = models.PurchaseItem
        fields = ["product", "unit", "quantity", "unit_price", "tax_percentage"]


PurchaseItemFormSet = inlineformset_factory(
    models.Purchase,
    models.PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
