from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import F, Sum
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BusinessProfile(TimeStampedModel):
    business_name = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100, blank=True)
    license_expiry_date = models.DateField(null=True, blank=True)
    vat_number = models.CharField(max_length=100, blank=True)
    vat_submission_date_1 = models.DateField(null=True, blank=True)
    vat_submission_date_2 = models.DateField(null=True, blank=True)
    vat_submission_date_3 = models.DateField(null=True, blank=True)
    vat_submission_date_4 = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    invoice_address = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.business_name


class Tax(TimeStampedModel):
    full_name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    percentage = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self) -> str:
        return self.full_name


class CustomerGroup(TimeStampedModel):
    group_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    invoice_address = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.group_name


class SocialMediaPlatform(models.TextChoices):
    FACEBOOK = "facebook", "Facebook"
    INSTAGRAM = "instagram", "Instagram"
    WECHAT = "wechat", "WeChat"
    TIKTOK = "tiktok", "TikTok"


class CustomerType(models.TextChoices):
    WHOLESALE = "wholesale", "Wholesale"
    RETAIL = "retail", "Retail"
    SOCIAL_MEDIA = "social_media", "Social Media"


class Customer(TimeStampedModel):
    name = models.CharField(max_length=255)
    customer_type = models.CharField(max_length=20, choices=CustomerType.choices)
    social_media_platform = models.CharField(
        max_length=20, choices=SocialMediaPlatform.choices, blank=True
    )
    social_media_handle = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    vat_number = models.CharField(max_length=100, blank=True)
    emirate = models.CharField(max_length=50, blank=True)
    google_map = models.URLField(blank=True)
    invoice_address = models.TextField(blank=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    customer_group = models.ForeignKey(
        CustomerGroup, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name


class Supplier(TimeStampedModel):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100, blank=True)
    mobile = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    vat_number = models.CharField(max_length=100, blank=True)
    invoice_address = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name


class CourierPartner(TimeStampedModel):
    name = models.CharField(max_length=255)
    invoice_address = models.TextField(blank=True)
    courier_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    settlement_cycle_days = models.PositiveIntegerField(default=30)

    def __str__(self) -> str:
        return self.name


class ExpenseGroup(TimeStampedModel):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class ExpenseType(TimeStampedModel):
    name = models.CharField(max_length=100)
    expense_group = models.ForeignKey(
        ExpenseGroup, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self) -> str:
        return self.name


class ReceiptType(TimeStampedModel):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    class ProductType(models.TextChoices):
        RAW_MATERIAL = "raw_material", "Raw Material"
        PRODUCT = "product", "Product"
        BOTH = "both", "Both"

    name = models.CharField(max_length=255)
    name_arabic = models.CharField(max_length=255, blank=True)
    product_type = models.CharField(
        max_length=20, choices=ProductType.choices, default=ProductType.PRODUCT
    )
    sku = models.CharField(max_length=100, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    base_unit = models.ForeignKey("Unit", on_delete=models.PROTECT, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_stock = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    taxes = models.ManyToManyField("Tax", blank=True, related_name="products")

    def __str__(self) -> str:
        return self.name


class Unit(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    short_name = models.CharField(max_length=20, blank=True)

    def __str__(self) -> str:
        return self.short_name or self.name


class ProductUnitPrice(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="unit_prices")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    conversion_factor = models.DecimalField(max_digits=14, decimal_places=4, default=1)
    sales_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ("product", "unit")

    def clean(self):
        if self.conversion_factor <= 0:
            raise ValidationError({"conversion_factor": "Conversion factor must be greater than 0."})

    def __str__(self) -> str:
        return f"{self.product.name} - {self.unit}"


class PaymentMode(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    BANK_TRANSFER = "bank_transfer", "Bank Transfer"
    CHEQUE = "cheque", "Cheque"


class OrderType(models.TextChoices):
    RETAIL = "retail", "Retail"
    WHOLESALE = "wholesale", "Wholesale"
    SOCIAL_MEDIA = "social_media", "Social Media"


class DeliveryMode(models.TextChoices):
    COURIER = "courier", "Courier"
    DIRECT = "direct", "Direct"


class SalesOrder(TimeStampedModel):
    order_number = models.CharField(max_length=30, unique=True, editable=False)
    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    transaction_mode = models.CharField(max_length=20, choices=PaymentMode.choices)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    customer_type_snapshot = models.CharField(max_length=20, blank=True)
    social_media_platform_snapshot = models.CharField(max_length=20, blank=True)
    delivery_mode = models.CharField(max_length=20, choices=DeliveryMode.choices)
    courier_partner = models.ForeignKey(
        CourierPartner, on_delete=models.SET_NULL, null=True, blank=True
    )
    courier_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        if self.customer:
            self.customer_type_snapshot = self.customer.customer_type
            self.social_media_platform_snapshot = self.customer.social_media_platform
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        today = timezone.now().strftime("%Y%m")
        prefix = f"SO-{today}-"
        last = (
            SalesOrder.objects.filter(order_number__startswith=prefix)
            .order_by("-order_number")
            .first()
        )
        if not last:
            return f"{prefix}0001"
        last_seq = int(last.order_number.split("-")[-1])
        return f"{prefix}{last_seq + 1:04d}"


class SalesOrderItem(TimeStampedModel):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0, editable=False)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def _get_conversion_factor(self) -> Decimal:
        if self.unit_id and self.product_id:
            unit_price = ProductUnitPrice.objects.filter(
                product_id=self.product_id, unit_id=self.unit_id
            ).first()
            if unit_price and unit_price.conversion_factor:
                return unit_price.conversion_factor
        return Decimal("1")

    def clean(self):
        if self.discount_amount and self.discount_amount < 0:
            raise ValidationError({"discount_amount": "Discount cannot be negative."})
        if self.product_id and self.discount_amount:
            max_discount = self.product.max_discount_amount or Decimal("0")
            if self.discount_amount > max_discount:
                raise ValidationError(
                    {"discount_amount": f"Maximum discount allowed is {max_discount}."}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        conversion_factor = self._get_conversion_factor()
        self.stock_quantity = (self.quantity or 0) * conversion_factor
        gross_total = (self.quantity or 0) * (self.unit_price or 0)
        self.line_total = gross_total - (self.discount_amount or 0)
        if self.line_total < 0:
            self.line_total = Decimal("0")

        old_stock_quantity = Decimal("0")
        old_product_id = self.product_id
        if self.pk:
            previous = SalesOrderItem.objects.filter(pk=self.pk).values(
                "stock_quantity", "product_id"
            ).first()
            if previous:
                old_stock_quantity = previous["stock_quantity"] or Decimal("0")
                old_product_id = previous["product_id"]

        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.product_id != old_product_id:
                Product.objects.filter(pk=old_product_id).update(
                    current_stock=F("current_stock") + old_stock_quantity
                )
                Product.objects.filter(pk=self.product_id).update(
                    current_stock=F("current_stock") - self.stock_quantity
                )
            else:
                stock_delta = old_stock_quantity - self.stock_quantity
                Product.objects.filter(pk=self.product_id).update(
                    current_stock=F("current_stock") + stock_delta
                )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            Product.objects.filter(pk=self.product_id).update(
                current_stock=F("current_stock") + (self.stock_quantity or 0)
            )
            super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.sales_order.order_number} - {self.product.name}"


class Sale(TimeStampedModel):
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.PROTECT)
    sale_date = models.DateField(default=timezone.now)
    courier_tracking_number = models.CharField(max_length=100, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"Sale {self.sales_order.order_number}"


class DeliveryStatus(TimeStampedModel):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    status = models.CharField(max_length=100)
    received_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    received_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"{self.sale.sales_order.order_number} - {self.status}"


class Receipt(TimeStampedModel):
    date = models.DateField(default=timezone.now)
    receipt_type = models.ForeignKey(ReceiptType, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mode = models.CharField(max_length=20, choices=PaymentMode.choices)
    cheque_number = models.CharField(max_length=100, blank=True)
    cheque_date = models.DateField(null=True, blank=True)
    bank = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"Receipt {self.id}"


class Payment(TimeStampedModel):
    date = models.DateField(default=timezone.now)
    payment_type = models.ForeignKey(ExpenseType, on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    courier_partner = models.ForeignKey(
        CourierPartner, on_delete=models.SET_NULL, null=True, blank=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mode = models.CharField(max_length=20, choices=PaymentMode.choices)
    bank = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=100, blank=True)
    cheque_number = models.CharField(max_length=100, blank=True)
    cheque_date = models.DateField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Payment {self.id}"


class DayClose(TimeStampedModel):
    date = models.DateField(default=timezone.now)
    opening_cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    opening_bank_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_receipts = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_cash_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    closing_bank_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"Day Close {self.date}"


class AssistantMessage(TimeStampedModel):
    question = models.TextField()
    answer = models.TextField()
    asked_by = models.CharField(max_length=150, blank=True)
    source = models.CharField(max_length=50, default="ai")

    def __str__(self) -> str:
        return f"AssistantMessage {self.id}"


class Production(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="productions")
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    stock_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0, editable=False)
    batch_number = models.CharField(max_length=100)
    production_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField(null=True, blank=True)

    def _get_conversion_factor(self) -> Decimal:
        if self.unit_id and self.product_id:
            unit_price = ProductUnitPrice.objects.filter(
                product_id=self.product_id, unit_id=self.unit_id
            ).first()
            if unit_price and unit_price.conversion_factor:
                return unit_price.conversion_factor
        return Decimal("1")

    def clean(self):
        if self.product and self.product.product_type == Product.ProductType.RAW_MATERIAL:
            raise ValidationError({"product": "Raw material cannot be added in production output."})
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than 0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        conversion_factor = self._get_conversion_factor()
        self.stock_quantity = (self.quantity or 0) * conversion_factor
        old_stock_quantity = Decimal("0")
        if self.pk:
            old_stock_quantity = (
                Production.objects.filter(pk=self.pk)
                .values_list("stock_quantity", flat=True)
                .first()
                or Decimal("0")
            )
        stock_delta = self.stock_quantity - old_stock_quantity
        with transaction.atomic():
            super().save(*args, **kwargs)
            Product.objects.filter(pk=self.product_id).update(
                current_stock=F("current_stock") + stock_delta
            )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            Product.objects.filter(pk=self.product_id).update(
                current_stock=F("current_stock") - (self.stock_quantity or 0)
            )
            super().delete(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.product.name} - {self.batch_number}"


class Purchase(TimeStampedModel):
    purchase_number = models.CharField(max_length=30, unique=True, editable=False)
    date = models.DateField(default=timezone.now)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT)
    invoice_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.purchase_number

    def save(self, *args, **kwargs):
        if not self.purchase_number:
            self.purchase_number = self._generate_purchase_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_purchase_number():
        today = timezone.now().strftime("%Y%m")
        prefix = f"PO-{today}-"
        last = (
            Purchase.objects.filter(purchase_number__startswith=prefix)
            .order_by("-purchase_number")
            .first()
        )
        if not last:
            return f"{prefix}0001"
        last_seq = int(last.purchase_number.split("-")[-1])
        return f"{prefix}{last_seq + 1:04d}"

    def recalculate_totals(self):
        totals = self.items.aggregate(
            subtotal=Sum("line_subtotal"), tax_total=Sum("line_tax_amount"), total=Sum("line_total")
        )
        self.subtotal = totals["subtotal"] or Decimal("0")
        self.tax_total = totals["tax_total"] or Decimal("0")
        self.grand_total = totals["total"] or Decimal("0")
        Purchase.objects.filter(pk=self.pk).update(
            subtotal=self.subtotal, tax_total=self.tax_total, grand_total=self.grand_total
        )


class PurchaseItem(TimeStampedModel):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    stock_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0, editable=False)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percentage = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    line_subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    line_tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)

    def _get_conversion_factor(self) -> Decimal:
        if self.unit_id and self.product_id:
            unit_price = ProductUnitPrice.objects.filter(
                product_id=self.product_id, unit_id=self.unit_id
            ).first()
            if unit_price and unit_price.conversion_factor:
                return unit_price.conversion_factor
        return Decimal("1")

    def clean(self):
        if self.product and self.product.product_type == Product.ProductType.PRODUCT:
            raise ValidationError({"product": "Finished product cannot be purchased as raw material."})
        if self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than 0."})
        if self.tax_percentage < 0:
            raise ValidationError({"tax_percentage": "Tax percentage cannot be negative."})

    def save(self, *args, **kwargs):
        self.full_clean()
        conversion_factor = self._get_conversion_factor()
        self.stock_quantity = (self.quantity or 0) * conversion_factor
        self.line_subtotal = (self.quantity or 0) * (self.unit_price or 0)
        self.line_tax_amount = self.line_subtotal * ((self.tax_percentage or 0) / Decimal("100"))
        self.line_total = self.line_subtotal + self.line_tax_amount
        old_stock_quantity = Decimal("0")
        old_product_id = self.product_id
        if self.pk:
            previous = PurchaseItem.objects.filter(pk=self.pk).values(
                "stock_quantity", "product_id"
            ).first()
            if previous:
                old_stock_quantity = previous["stock_quantity"] or Decimal("0")
                old_product_id = previous["product_id"]

        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.product_id != old_product_id:
                Product.objects.filter(pk=old_product_id).update(
                    current_stock=F("current_stock") - old_stock_quantity
                )
                Product.objects.filter(pk=self.product_id).update(
                    current_stock=F("current_stock") + self.stock_quantity
                )
            else:
                stock_delta = self.stock_quantity - old_stock_quantity
                Product.objects.filter(pk=self.product_id).update(
                    current_stock=F("current_stock") + stock_delta
                )
            self.purchase.recalculate_totals()

    def delete(self, *args, **kwargs):
        purchase = self.purchase
        with transaction.atomic():
            Product.objects.filter(pk=self.product_id).update(
                current_stock=F("current_stock") - (self.stock_quantity or 0)
            )
            super().delete(*args, **kwargs)
            purchase.recalculate_totals()

    def __str__(self) -> str:
        return f"{self.purchase.purchase_number} - {self.product.name}"

# Create your models here.
