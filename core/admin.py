from django.contrib import admin
from hoc.admin_site import admin_site
from . import models


@admin.register(models.BusinessProfile, site=admin_site)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ("business_name", "license_number", "vat_number", "contact_number", "email")


@admin.register(models.Tax, site=admin_site)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("full_name", "short_name", "percentage", "fixed_amount")


@admin.register(models.CustomerGroup, site=admin_site)
class CustomerGroupAdmin(admin.ModelAdmin):
    list_display = ("group_name", "contact_person", "mobile", "email")


@admin.register(models.Customer, site=admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "customer_type", "mobile", "email", "emirate")
    search_fields = ("name", "mobile", "email")


@admin.register(models.Supplier, site=admin_site)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_person", "mobile", "email")


@admin.register(models.CourierPartner, site=admin_site)
class CourierPartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "courier_fee", "settlement_cycle_days")


@admin.register(models.ExpenseGroup, site=admin_site)
class ExpenseGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(models.ExpenseType, site=admin_site)
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "expense_group")


@admin.register(models.ReceiptType, site=admin_site)
class ReceiptTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(models.Product, site=admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "name_arabic",
        "product_type",
        "sku",
        "barcode",
        "unit_price",
        "max_discount_amount",
        "current_stock",
    )
    search_fields = ("name", "name_arabic", "sku", "barcode")
    list_filter = ("product_type",)


@admin.register(models.Unit, site=admin_site)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name")
    search_fields = ("name", "short_name")


class ProductUnitPriceInline(admin.TabularInline):
    model = models.ProductUnitPrice
    extra = 1


ProductAdmin.inlines = [ProductUnitPriceInline]


class SalesOrderItemInline(admin.TabularInline):
    model = models.SalesOrderItem
    extra = 1
    fields = ("product", "unit", "quantity", "unit_price", "discount_amount", "line_total")
    readonly_fields = ("line_total",)


@admin.register(models.SalesOrder, site=admin_site)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "order_type", "customer", "delivery_mode", "net_price")
    search_fields = ("order_number", "customer__name")
    inlines = [SalesOrderItemInline]


@admin.register(models.Sale, site=admin_site)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("sales_order", "sale_date", "total_amount", "courier_tracking_number")


@admin.register(models.DeliveryStatus, site=admin_site)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = ("sale", "status", "received_amount", "received_date")


@admin.register(models.Receipt, site=admin_site)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ("date", "receipt_type", "customer", "amount", "mode")


@admin.register(models.Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("date", "payment_type", "supplier", "amount", "mode")


@admin.register(models.DayClose, site=admin_site)
class DayCloseAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "opening_cash_balance",
        "opening_bank_balance",
        "closing_cash_balance",
        "closing_bank_balance",
    )


@admin.register(models.AssistantMessage, site=admin_site)
class AssistantMessageAdmin(admin.ModelAdmin):
    list_display = ("created_at", "asked_by", "source")
    search_fields = ("question", "answer", "asked_by")


@admin.register(models.Production, site=admin_site)
class ProductionAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "batch_number",
        "production_date",
        "expiry_date",
        "quantity",
        "unit",
        "stock_quantity",
    )
    search_fields = ("product__name", "batch_number")
    list_filter = ("production_date", "expiry_date")


class PurchaseItemInline(admin.TabularInline):
    model = models.PurchaseItem
    extra = 1
    fields = (
        "product",
        "unit",
        "quantity",
        "unit_price",
        "tax_percentage",
        "line_subtotal",
        "line_tax_amount",
        "line_total",
    )
    readonly_fields = ("line_subtotal", "line_tax_amount", "line_total")


@admin.register(models.Purchase, site=admin_site)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "purchase_number",
        "date",
        "supplier",
        "subtotal",
        "tax_total",
        "grand_total",
    )
    search_fields = ("purchase_number", "supplier__name", "invoice_number")
    list_filter = ("date", "supplier")
    readonly_fields = ("purchase_number", "subtotal", "tax_total", "grand_total")
    inlines = [PurchaseItemInline]

# Register your models here.
