from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import FieldDoesNotExist
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from django.forms import modelform_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
import json
from datetime import datetime, timedelta

from . import models
from .forms import ProductForm, ProductUnitPriceFormSet, PurchaseForm, PurchaseItemFormSet
from .reports import REPORT_LABELS


def _module_item(
    slug,
    title,
    model,
    fields=None,
    list_display=None,
    order_by="-created_at",
    supports_inline_items=False,
):
    return {
        "slug": slug,
        "title": title,
        "model": model,
        "fields": fields,
        "list_display": list_display or [],
        "order_by": order_by,
        "supports_inline_items": supports_inline_items,
    }


MODULES = {
    "business-profile": _module_item(
        "business-profile",
        "Business Profile",
        models.BusinessProfile,
        fields=[
            "business_name",
            "license_number",
            "license_expiry_date",
            "vat_number",
            "contact_number",
            "email",
            "invoice_address",
        ],
        list_display=["business_name", "vat_number", "contact_number", "email"],
    ),
    "taxes": _module_item("taxes", "Taxes", models.Tax, list_display=["full_name", "short_name", "percentage"]),
    "customer-groups": _module_item(
        "customer-groups",
        "Customer Groups",
        models.CustomerGroup,
        list_display=["group_name", "contact_person", "mobile", "email"],
    ),
    "customers": _module_item(
        "customers",
        "Customers",
        models.Customer,
        list_display=["name", "customer_type", "mobile", "email"],
    ),
    "suppliers": _module_item(
        "suppliers",
        "Suppliers",
        models.Supplier,
        list_display=["name", "contact_person", "mobile", "email"],
    ),
    "courier-partners": _module_item(
        "courier-partners",
        "Courier Partners",
        models.CourierPartner,
        list_display=["name", "courier_fee", "settlement_cycle_days"],
    ),
    "expense-groups": _module_item("expense-groups", "Expense Groups", models.ExpenseGroup, list_display=["name"]),
    "expense-types": _module_item(
        "expense-types",
        "Expense Types",
        models.ExpenseType,
        list_display=["name", "expense_group"],
    ),
    "receipt-types": _module_item("receipt-types", "Receipt Types", models.ReceiptType, list_display=["name"]),
    "products": _module_item(
        "products",
        "Products",
        models.Product,
        fields=[
            "name",
            "name_arabic",
            "product_type",
            "barcode",
            "base_unit",
            "taxes",
            "unit_price",
            "max_discount_amount",
        ],
        list_display=["name", "product_type", "base_unit", "barcode", "unit_price", "current_stock"],
    ),
    "units": _module_item("units", "Units", models.Unit, list_display=["name", "short_name"]),
    "sales-orders": _module_item(
        "sales-orders",
        "Sales Orders",
        models.SalesOrder,
        fields=[
            "order_type",
            "transaction_mode",
            "customer",
            "delivery_mode",
            "courier_partner",
            "courier_fee",
            "net_price",
        ],
        list_display=["order_number", "order_type", "customer", "delivery_mode", "net_price"],
    ),
    "sales": _module_item(
        "sales",
        "Sales",
        models.Sale,
        list_display=["sales_order", "sale_date", "total_amount", "courier_tracking_number"],
    ),
    "delivery-status": _module_item(
        "delivery-status",
        "Delivery Status",
        models.DeliveryStatus,
        list_display=["sale", "status", "received_amount", "received_date"],
    ),
    "receipts": _module_item(
        "receipts",
        "Receipts",
        models.Receipt,
        list_display=["date", "receipt_type", "customer", "amount", "mode"],
    ),
    "payments": _module_item(
        "payments",
        "Payments",
        models.Payment,
        list_display=["date", "payment_type", "supplier", "amount", "mode"],
    ),
    "day-close": _module_item(
        "day-close",
        "Day Close",
        models.DayClose,
        list_display=["date", "opening_cash_balance", "closing_cash_balance", "closing_bank_balance"],
    ),
    "production": _module_item(
        "production",
        "Production",
        models.Production,
        list_display=["product", "batch_number", "production_date", "quantity", "stock_quantity"],
    ),
    "purchases": _module_item(
        "purchases",
        "Purchases",
        models.Purchase,
        fields=["date", "supplier", "invoice_number", "notes"],
        list_display=["purchase_number", "date", "supplier", "subtotal", "tax_total", "grand_total"],
        supports_inline_items=True,
    ),
}

REPORT_MENU_ITEMS = [
    {"title": label, "url": f"/reports/{slug}/", "icon": "feather icon-file-text"} for slug, label in REPORT_LABELS.items()
]

MODULE_GROUPS = [
    {
        "title": "Overview",
        "items": [{"title": "Dashboard", "url": "/backend/"}],
    },
    {
        "title": "Master Data",
        "items": [
            {"title": MODULES["business-profile"]["title"], "url": "/backend/modules/business-profile/"},
            {"title": MODULES["taxes"]["title"], "url": "/backend/modules/taxes/"},
            {"title": MODULES["customer-groups"]["title"], "url": "/backend/modules/customer-groups/"},
            {"title": MODULES["customers"]["title"], "url": "/backend/modules/customers/"},
            {"title": MODULES["suppliers"]["title"], "url": "/backend/modules/suppliers/"},
            {"title": MODULES["courier-partners"]["title"], "url": "/backend/modules/courier-partners/"},
            {"title": MODULES["expense-groups"]["title"], "url": "/backend/modules/expense-groups/"},
            {"title": MODULES["expense-types"]["title"], "url": "/backend/modules/expense-types/"},
            {"title": MODULES["receipt-types"]["title"], "url": "/backend/modules/receipt-types/"},
            {"title": MODULES["products"]["title"], "url": "/backend/modules/products/"},
            {"title": MODULES["units"]["title"], "url": "/backend/modules/units/"},
        ],
    },
    {
        "title": "Transactions",
        "items": [
            {"title": MODULES["sales-orders"]["title"], "url": "/backend/modules/sales-orders/"},
            {"title": MODULES["sales"]["title"], "url": "/backend/modules/sales/"},
            {"title": MODULES["delivery-status"]["title"], "url": "/backend/modules/delivery-status/"},
            {"title": MODULES["receipts"]["title"], "url": "/backend/modules/receipts/"},
            {"title": MODULES["payments"]["title"], "url": "/backend/modules/payments/"},
            {"title": MODULES["day-close"]["title"], "url": "/backend/modules/day-close/"},
            {"title": MODULES["production"]["title"], "url": "/backend/modules/production/"},
            {"title": MODULES["purchases"]["title"], "url": "/backend/modules/purchases/"},
        ],
    },
    {
        "title": "Tools",
        "items": [
            {"title": "Reports", "url": "/reports/", "children": REPORT_MENU_ITEMS},
            {"title": "Admin", "url": "/admin/"},
            {"title": "API", "url": "/api/"},
        ],
    },
]

NAV_ICONS = {
    "Dashboard": "feather icon-home",
    "Business Profile": "feather icon-briefcase",
    "Taxes": "feather icon-percent",
    "Customer Groups": "feather icon-users",
    "Customers": "feather icon-user",
    "Suppliers": "feather icon-truck",
    "Courier Partners": "feather icon-package",
    "Expense Groups": "feather icon-layers",
    "Expense Types": "feather icon-credit-card",
    "Receipt Types": "feather icon-file",
    "Products": "feather icon-box",
    "Units": "feather icon-hash",
    "Sales Orders": "feather icon-shopping-cart",
    "Sales": "feather icon-bar-chart-2",
    "Delivery Status": "feather icon-navigation",
    "Receipts": "feather icon-download",
    "Payments": "feather icon-upload",
    "Day Close": "feather icon-clock",
    "Production": "feather icon-settings",
    "Purchases": "feather icon-shopping-bag",
    "Reports": "feather icon-pie-chart",
    "Admin": "feather icon-shield",
    "API": "feather icon-code",
}


def _apply_nav_icons():
    for group in MODULE_GROUPS:
        for item in group.get("items", []):
            item.setdefault("icon", NAV_ICONS.get(item.get("title"), "feather icon-circle"))
            for child in item.get("children", []):
                child.setdefault("icon", "feather icon-file-text")


_apply_nav_icons()


def _module(slug):
    module = MODULES.get(slug)
    if not module:
        raise Http404("Unknown module")
    return module


def _safe_value(obj, field_name):
    try:
        field = obj._meta.get_field(field_name)
    except FieldDoesNotExist:
        return ""
    value = getattr(obj, field_name)
    if hasattr(field, "choices") and field.choices:
        display_attr = f"get_{field_name}_display"
        if hasattr(obj, display_attr):
            return getattr(obj, display_attr)()
    return value


def _backend_context(extra=None):
    data = {"module_groups": MODULE_GROUPS}
    if extra:
        data.update(extra)
    return data


def _build_dashboard_metrics():
    now = timezone.now()
    this_month_orders = models.SalesOrder.objects.filter(
        created_at__year=now.year, created_at__month=now.month
    ).count()
    this_month_sales_value = (
        models.Sale.objects.filter(sale_date__year=now.year, sale_date__month=now.month).aggregate(
            total=Sum("total_amount")
        )["total"]
        or 0
    )

    products = models.Product.objects.all()
    stock_value = sum((p.current_stock or 0) * (p.unit_price or 0) for p in products)

    week_start = (now - timedelta(days=6)).date()
    sales_by_day_qs = (
        models.Sale.objects.filter(sale_date__gte=week_start, sale_date__lte=now.date())
        .annotate(day=TruncDay("sale_date"))
        .values("day")
        .annotate(total=Sum("total_amount"))
        .order_by("day")
    )
    sales_by_day_map = {}
    for row in sales_by_day_qs:
        day_value = row["day"]
        day_key = day_value.date() if hasattr(day_value, "date") else day_value
        sales_by_day_map[day_key] = float(row["total"] or 0)
    sales_week_labels = []
    sales_week_values = []
    for i in range(7):
        day = (now - timedelta(days=6 - i)).date()
        sales_week_labels.append(day.strftime("%a"))
        sales_week_values.append(sales_by_day_map.get(day, 0.0))

    sales_by_month_qs = (
        models.Sale.objects.filter(sale_date__year=now.year)
        .annotate(month=TruncMonth("sale_date"))
        .values("month")
        .annotate(total=Sum("total_amount"))
        .order_by("month")
    )
    sales_by_month_map = {row["month"].month: float(row["total"] or 0) for row in sales_by_month_qs}
    sales_month_labels = []
    sales_month_values = []
    for month in range(1, 13):
        sales_month_labels.append(datetime(2000, month, 1).strftime("%b"))
        sales_month_values.append(sales_by_month_map.get(month, 0.0))

    healthy_stock_count = models.Product.objects.filter(current_stock__gt=10).count()
    low_stock_count = models.Product.objects.filter(current_stock__gt=0, current_stock__lte=10).count()
    out_of_stock_count = models.Product.objects.filter(current_stock__lte=0).count()

    return {
        "customer_count": models.Customer.objects.count(),
        "order_count": models.SalesOrder.objects.count(),
        "sale_count": models.Sale.objects.count(),
        "total_receipts": models.Receipt.objects.count(),
        "product_count": models.Product.objects.count(),
        "purchase_count": models.Purchase.objects.count(),
        "production_count": models.Production.objects.count(),
        "stock_value": stock_value,
        "sales_value": models.Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0,
        "receipt_value": models.Receipt.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "payment_value": models.Payment.objects.aggregate(total=Sum("amount"))["total"] or 0,
        "purchase_value": models.Purchase.objects.aggregate(total=Sum("grand_total"))["total"] or 0,
        "total_stock_units": models.Product.objects.aggregate(total=Sum("current_stock"))["total"] or 0,
        "out_of_stock_count": out_of_stock_count,
        "low_stock_count": low_stock_count,
        "this_month_orders": this_month_orders,
        "this_month_sales_value": this_month_sales_value,
        "latest_orders": models.SalesOrder.objects.select_related("customer")
        .order_by("-created_at")[:8],
        "latest_purchases": models.Purchase.objects.select_related("supplier").order_by("-created_at")[:6],
        "latest_receipts": models.Receipt.objects.select_related("customer").order_by("-date", "-created_at")[:6],
        "low_stock_products": models.Product.objects.filter(current_stock__lte=10).order_by(
            "current_stock", "name"
        )[:8],
        "sales_week_labels_json": json.dumps(sales_week_labels),
        "sales_week_values_json": json.dumps(sales_week_values),
        "sales_month_labels_json": json.dumps(sales_month_labels),
        "sales_month_values_json": json.dumps(sales_month_values),
        "stock_pie_labels_json": json.dumps(["Healthy", "Low", "Out"]),
        "stock_pie_values_json": json.dumps([healthy_stock_count, low_stock_count, out_of_stock_count]),
    }


def _style_form(form):
    for field in form.fields.values():
        widget = field.widget
        current = widget.attrs.get("class", "")
        if widget.__class__.__name__.lower().find("select") >= 0:
            css = "custom-select"
        elif widget.__class__.__name__.lower().find("checkbox") >= 0:
            css = "form-check-input"
        else:
            css = "form-control"
        widget.attrs["class"] = (current + " " + css).strip()
    return form


def _style_formset(formset):
    for f in formset.forms:
        _style_form(f)
    return formset


def dashboard(request):
    context = _build_dashboard_metrics()
    return render(request, "dashboard.html", context)


@staff_member_required
def backend_home(request):
    context = _backend_context(_build_dashboard_metrics())
    return render(request, "backend/home.html", context)


@staff_member_required
def backend_module_list(request, module_slug):
    module = _module(module_slug)
    if module["supports_inline_items"]:
        return purchase_list(request)

    model = module["model"]
    rows = model.objects.all().order_by(module["order_by"])[:120]
    list_display = module["list_display"] or [f.name for f in model._meta.fields[:5]]
    table_rows = [{"obj": row, "values": [_safe_value(row, col) for col in list_display]} for row in rows]

    context = _backend_context(
        {
            "module": module,
            "list_display": list_display,
            "table_rows": table_rows,
        }
    )
    return render(request, "backend/module_list.html", context)


def _product_form_context(module, form, unit_price_formset, is_create, obj=None):
    data = {
        "module": module,
        "form": form,
        "product_unit_price_formset": unit_price_formset,
        "is_create": is_create,
    }
    if obj is not None:
        data["obj"] = obj
    return _backend_context(data)


def _sync_product_base_unit_price(product):
    if not product.base_unit_id:
        return
    models.ProductUnitPrice.objects.update_or_create(
        product=product,
        unit=product.base_unit,
        defaults={
            "conversion_factor": 1,
            "sales_price": product.unit_price or 0,
        },
    )


@staff_member_required
def product_create(request, module):
    if request.method == "POST":
        form = _style_form(ProductForm(request.POST))
        formset = _style_formset(
            ProductUnitPriceFormSet(request.POST, instance=models.Product(), prefix="unit_prices")
        )
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = form.save()
                formset.instance = product
                formset.save()
                _sync_product_base_unit_price(product)
            messages.success(request, "Products entry created.")
            return redirect("backend_module_list", module_slug="products")
    else:
        form = _style_form(ProductForm())
        formset = _style_formset(ProductUnitPriceFormSet(instance=models.Product(), prefix="unit_prices"))

    context = _product_form_context(module, form, formset, is_create=True)
    return render(request, "backend/module_form.html", context)


@staff_member_required
def product_edit(request, module, obj):
    if request.method == "POST":
        form = _style_form(ProductForm(request.POST, instance=obj))
        formset = _style_formset(
            ProductUnitPriceFormSet(request.POST, instance=obj, prefix="unit_prices")
        )
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                product = form.save()
                formset.save()
                _sync_product_base_unit_price(product)
            messages.success(request, "Products updated.")
            return redirect("backend_module_list", module_slug="products")
    else:
        form = _style_form(ProductForm(instance=obj))
        formset = _style_formset(ProductUnitPriceFormSet(instance=obj, prefix="unit_prices"))

    context = _product_form_context(module, form, formset, is_create=False, obj=obj)
    return render(request, "backend/module_form.html", context)


@staff_member_required
def backend_module_create(request, module_slug):
    module = _module(module_slug)
    if module["supports_inline_items"]:
        return purchase_create(request)
    if module_slug == "products":
        return product_create(request, module)

    model = module["model"]
    form_class = modelform_factory(model, fields=module["fields"] or "__all__")
    if request.method == "POST":
        form = _style_form(form_class(request.POST))
        if form.is_valid():
            form.save()
            messages.success(request, f"{module['title']} entry created.")
            return redirect("backend_module_list", module_slug=module_slug)
    else:
        form = _style_form(form_class())

    context = _backend_context({"module": module, "form": form, "is_create": True})
    return render(request, "backend/module_form.html", context)


@staff_member_required
def backend_module_edit(request, module_slug, pk):
    module = _module(module_slug)
    if module["supports_inline_items"]:
        return purchase_edit(request, pk)

    model = module["model"]
    obj = get_object_or_404(model, pk=pk)
    if module_slug == "products":
        return product_edit(request, module, obj)
    form_class = modelform_factory(model, fields=module["fields"] or "__all__")

    if request.method == "POST":
        form = _style_form(form_class(request.POST, instance=obj))
        if form.is_valid():
            form.save()
            messages.success(request, f"{module['title']} updated.")
            return redirect("backend_module_list", module_slug=module_slug)
    else:
        form = _style_form(form_class(instance=obj))

    context = _backend_context({"module": module, "form": form, "obj": obj, "is_create": False})
    return render(request, "backend/module_form.html", context)


@staff_member_required
def backend_module_delete(request, module_slug, pk):
    module = _module(module_slug)
    if module_slug == "business-profile":
        messages.warning(request, "Business Profile cannot be deleted.")
        return redirect("backend_module_list", module_slug=module_slug)
    if module["supports_inline_items"]:
        return purchase_delete(request, pk)

    model = module["model"]
    obj = get_object_or_404(model, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, f"{module['title']} deleted.")
        return redirect("backend_module_list", module_slug=module_slug)

    context = _backend_context({"module": module, "obj": obj})
    return render(request, "backend/module_delete.html", context)


@staff_member_required
def purchase_list(request):
    rows = models.Purchase.objects.select_related("supplier").order_by("-created_at")[:120]
    context = _backend_context(
        {
            "module": MODULES["purchases"],
            "rows": rows,
        }
    )
    return render(request, "backend/purchases_list.html", context)


@staff_member_required
def purchase_create(request):
    if request.method == "POST":
        purchase_form = _style_form(PurchaseForm(request.POST))
        purchase = models.Purchase()
        item_formset = _style_formset(PurchaseItemFormSet(request.POST, instance=purchase, prefix="items"))
        if purchase_form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                purchase = purchase_form.save()
                item_formset.instance = purchase
                item_formset.save()
            messages.success(request, "Purchase entry created.")
            return redirect("backend_module_list", module_slug="purchases")
    else:
        purchase_form = _style_form(PurchaseForm())
        item_formset = _style_formset(PurchaseItemFormSet(instance=models.Purchase(), prefix="items"))

    context = _backend_context(
        {
            "module": MODULES["purchases"],
            "purchase_form": purchase_form,
            "item_formset": item_formset,
            "is_create": True,
        }
    )
    return render(request, "backend/purchase_form.html", context)


@staff_member_required
def purchase_edit(request, pk):
    purchase = get_object_or_404(models.Purchase, pk=pk)
    if request.method == "POST":
        purchase_form = _style_form(PurchaseForm(request.POST, instance=purchase))
        item_formset = _style_formset(PurchaseItemFormSet(request.POST, instance=purchase, prefix="items"))
        if purchase_form.is_valid() and item_formset.is_valid():
            with transaction.atomic():
                purchase_form.save()
                item_formset.save()
            messages.success(request, "Purchase updated.")
            return redirect("backend_module_list", module_slug="purchases")
    else:
        purchase_form = _style_form(PurchaseForm(instance=purchase))
        item_formset = _style_formset(PurchaseItemFormSet(instance=purchase, prefix="items"))

    context = _backend_context(
        {
            "module": MODULES["purchases"],
            "purchase_form": purchase_form,
            "item_formset": item_formset,
            "purchase": purchase,
            "is_create": False,
        }
    )
    return render(request, "backend/purchase_form.html", context)


@staff_member_required
def purchase_delete(request, pk):
    purchase = get_object_or_404(models.Purchase, pk=pk)
    if request.method == "POST":
        purchase.delete()
        messages.success(request, "Purchase deleted.")
        return redirect("backend_module_list", module_slug="purchases")

    context = _backend_context({"module": MODULES["purchases"], "obj": purchase})
    return render(request, "backend/module_delete.html", context)
