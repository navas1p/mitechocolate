from datetime import date

from django.db.models import F, Sum
from django.db.models.functions import Coalesce, TruncDay, TruncMonth, TruncWeek

from . import models


def _date_range(qs, field: str, start: date | None, end: date | None):
    if start:
        qs = qs.filter(**{f"{field}__gte": start})
    if end:
        qs = qs.filter(**{f"{field}__lte": end})
    return qs


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def basic_report(question: str) -> str | None:
    q = (question or "").lower()

    if "sales" in q or "revenue" in q:
        total_sales = models.Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0
        count = models.Sale.objects.count()
        return f"Total sales: {total_sales:.2f} across {count} sales records."

    if "receipt" in q or "receipts" in q or "collection" in q:
        total_receipts = models.Receipt.objects.aggregate(total=Sum("amount"))["total"] or 0
        count = models.Receipt.objects.count()
        return f"Total receipts: {total_receipts:.2f} across {count} receipts."

    if "payment" in q or "payments" in q or "expense" in q:
        total_payments = models.Payment.objects.aggregate(total=Sum("amount"))["total"] or 0
        count = models.Payment.objects.count()
        return f"Total payments: {total_payments:.2f} across {count} payments."

    if "outstanding" in q or "due" in q or "balance" in q:
        sales_total = models.Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0
        receipts_total = models.Receipt.objects.aggregate(total=Sum("amount"))["total"] or 0
        outstanding = sales_total - receipts_total
        return (
            "Estimated outstanding balance (sales minus receipts): "
            f"{outstanding:.2f}. This is a high-level estimate."
        )

    if "courier" in q or "delivery" in q:
        courier_sales = models.SalesOrder.objects.filter(delivery_mode=models.DeliveryMode.COURIER)
        courier_fees = courier_sales.aggregate(total=Sum("courier_fee"))["total"] or 0
        collected = (
            models.DeliveryStatus.objects.aggregate(total=Sum("received_amount"))["total"] or 0
        )
        return (
            f"Courier fees total: {courier_fees:.2f}. "
            f"Collected from deliveries: {collected:.2f}."
        )

    return None


def get_filters(params):
    return {
        "start_date": _parse_date(params.get("start_date")),
        "end_date": _parse_date(params.get("end_date")),
        "customer_id": params.get("customer_id") or None,
        "customer_group_id": params.get("customer_group_id") or None,
        "courier_partner_id": params.get("courier_partner_id") or None,
        "product_id": params.get("product_id") or None,
        "order_type": params.get("order_type") or None,
        "payment_mode": params.get("payment_mode") or None,
        "group_by": params.get("group_by") or "month",
    }


def report_sales_summary(filters):
    qs = models.Sale.objects.select_related("sales_order", "sales_order__customer")
    qs = _date_range(qs, "sale_date", filters["start_date"], filters["end_date"])
    if filters["customer_id"]:
        qs = qs.filter(sales_order__customer_id=filters["customer_id"])
    if filters["customer_group_id"]:
        qs = qs.filter(sales_order__customer__customer_group_id=filters["customer_group_id"])
    if filters["order_type"]:
        qs = qs.filter(sales_order__order_type=filters["order_type"])

    group_by = filters["group_by"]
    trunc = TruncMonth("sale_date")
    if group_by == "day":
        trunc = TruncDay("sale_date")
    elif group_by == "week":
        trunc = TruncWeek("sale_date")

    data = (
        qs.annotate(period=trunc)
        .values("period")
        .annotate(total=Sum(Coalesce("total_amount", F("sales_order__net_price"))))
        .order_by("period")
    )
    headers = ["Period", "Total Sales"]
    rows = [[row["period"], f'{row["total"] or 0:.2f}'] for row in data]
    return "Sales Summary", headers, rows


def report_sales_by_customer_group(filters):
    qs = models.Sale.objects.select_related("sales_order__customer__customer_group")
    qs = _date_range(qs, "sale_date", filters["start_date"], filters["end_date"])
    if filters["customer_group_id"]:
        qs = qs.filter(sales_order__customer__customer_group_id=filters["customer_group_id"])
    if filters["order_type"]:
        qs = qs.filter(sales_order__order_type=filters["order_type"])
    data = (
        qs.values("sales_order__customer__customer_group__group_name")
        .annotate(total=Sum(Coalesce("total_amount", F("sales_order__net_price"))))
        .order_by("sales_order__customer__customer_group__group_name")
    )
    headers = ["Customer Group", "Total Sales"]
    rows = [
        [row["sales_order__customer__customer_group__group_name"] or "Unassigned",
         f'{row["total"] or 0:.2f}']
        for row in data
    ]
    return "Sales by Customer Group", headers, rows


def report_sales_by_customer(filters):
    qs = models.Sale.objects.select_related("sales_order__customer")
    qs = _date_range(qs, "sale_date", filters["start_date"], filters["end_date"])
    if filters["customer_id"]:
        qs = qs.filter(sales_order__customer_id=filters["customer_id"])
    if filters["customer_group_id"]:
        qs = qs.filter(sales_order__customer__customer_group_id=filters["customer_group_id"])
    if filters["order_type"]:
        qs = qs.filter(sales_order__order_type=filters["order_type"])
    data = (
        qs.values("sales_order__customer__name")
        .annotate(total=Sum(Coalesce("total_amount", F("sales_order__net_price"))))
        .order_by("sales_order__customer__name")
    )
    headers = ["Customer", "Total Sales"]
    rows = [[row["sales_order__customer__name"], f'{row["total"] or 0:.2f}'] for row in data]
    return "Sales by Customer", headers, rows


def report_sales_by_product(filters):
    qs = models.SalesOrderItem.objects.select_related(
        "sales_order", "sales_order__sale", "product"
    )
    qs = qs.filter(sales_order__sale__isnull=False)
    qs = _date_range(qs, "sales_order__sale__sale_date", filters["start_date"], filters["end_date"])
    if filters["product_id"]:
        qs = qs.filter(product_id=filters["product_id"])
    if filters["customer_id"]:
        qs = qs.filter(sales_order__customer_id=filters["customer_id"])
    if filters["customer_group_id"]:
        qs = qs.filter(sales_order__customer__customer_group_id=filters["customer_group_id"])
    if filters["order_type"]:
        qs = qs.filter(sales_order__order_type=filters["order_type"])
    data = (
        qs.values("product__name")
        .annotate(quantity=Sum("quantity"), total=Sum("line_total"))
        .order_by("product__name")
    )
    headers = ["Product", "Quantity", "Total Sales"]
    rows = [
        [row["product__name"], f'{row["quantity"] or 0:.2f}', f'{row["total"] or 0:.2f}']
        for row in data
    ]
    return "Sales by Product", headers, rows


def report_sales_by_courier(filters):
    qs = models.Sale.objects.select_related("sales_order__courier_partner")
    qs = qs.filter(sales_order__delivery_mode=models.DeliveryMode.COURIER)
    qs = _date_range(qs, "sale_date", filters["start_date"], filters["end_date"])
    if filters["courier_partner_id"]:
        qs = qs.filter(sales_order__courier_partner_id=filters["courier_partner_id"])
    data = (
        qs.values("sales_order__courier_partner__name")
        .annotate(total=Sum(Coalesce("total_amount", F("sales_order__net_price"))))
        .order_by("sales_order__courier_partner__name")
    )
    headers = ["Courier Partner", "Total Sales"]
    rows = [
        [row["sales_order__courier_partner__name"] or "Unassigned",
         f'{row["total"] or 0:.2f}']
        for row in data
    ]
    return "Sales by Courier Partner", headers, rows


def report_outstanding_by_customer(filters):
    sales_qs = models.Sale.objects.select_related("sales_order__customer")
    sales_qs = _date_range(sales_qs, "sale_date", filters["start_date"], filters["end_date"])
    if filters["customer_id"]:
        sales_qs = sales_qs.filter(sales_order__customer_id=filters["customer_id"])
    if filters["customer_group_id"]:
        sales_qs = sales_qs.filter(sales_order__customer__customer_group_id=filters["customer_group_id"])
    sales = (
        sales_qs.values("sales_order__customer_id", "sales_order__customer__name")
        .annotate(total=Sum(Coalesce("total_amount", F("sales_order__net_price"))))
    )

    receipts_qs = models.Receipt.objects.select_related("customer")
    receipts_qs = _date_range(receipts_qs, "date", filters["start_date"], filters["end_date"])
    if filters["customer_id"]:
        receipts_qs = receipts_qs.filter(customer_id=filters["customer_id"])
    if filters["customer_group_id"]:
        receipts_qs = receipts_qs.filter(customer__customer_group_id=filters["customer_group_id"])
    receipts = receipts_qs.values("customer_id").annotate(total=Sum("amount"))

    receipts_map = {r["customer_id"]: r["total"] or 0 for r in receipts}
    rows = []
    for s in sales:
        received = receipts_map.get(s["sales_order__customer_id"], 0)
        outstanding = (s["total"] or 0) - received
        rows.append([s["sales_order__customer__name"], f"{outstanding:.2f}"])

    headers = ["Customer", "Outstanding"]
    return "Outstanding by Customer", headers, rows


def report_outstanding_by_customer_group(filters):
    sales_qs = models.Sale.objects.select_related("sales_order__customer__customer_group")
    sales_qs = _date_range(sales_qs, "sale_date", filters["start_date"], filters["end_date"])
    if filters["customer_group_id"]:
        sales_qs = sales_qs.filter(sales_order__customer__customer_group_id=filters["customer_group_id"])
    sales = (
        sales_qs.values(
            "sales_order__customer__customer_group_id",
            "sales_order__customer__customer_group__group_name",
        )
        .annotate(total=Sum(Coalesce("total_amount", F("sales_order__net_price"))))
    )

    receipts_qs = models.Receipt.objects.select_related("customer__customer_group")
    receipts_qs = _date_range(receipts_qs, "date", filters["start_date"], filters["end_date"])
    if filters["customer_group_id"]:
        receipts_qs = receipts_qs.filter(customer__customer_group_id=filters["customer_group_id"])
    receipts = receipts_qs.values("customer__customer_group_id").annotate(total=Sum("amount"))

    receipts_map = {r["customer__customer_group_id"]: r["total"] or 0 for r in receipts}
    rows = []
    for s in sales:
        received = receipts_map.get(s["sales_order__customer__customer_group_id"], 0)
        outstanding = (s["total"] or 0) - received
        rows.append([s["sales_order__customer__customer_group__group_name"] or "Unassigned",
                     f"{outstanding:.2f}"])

    headers = ["Customer Group", "Outstanding"]
    return "Outstanding by Customer Group", headers, rows


def report_receipts_by_mode(filters):
    qs = models.Receipt.objects.all()
    qs = _date_range(qs, "date", filters["start_date"], filters["end_date"])
    if filters["payment_mode"]:
        qs = qs.filter(mode=filters["payment_mode"])
    data = qs.values("mode").annotate(total=Sum("amount")).order_by("mode")
    headers = ["Mode", "Total Receipts"]
    rows = [[row["mode"], f'{row["total"] or 0:.2f}'] for row in data]
    return "Receipts by Mode", headers, rows


def report_payments_by_expense(filters):
    qs = models.Payment.objects.select_related("payment_type__expense_group")
    qs = _date_range(qs, "date", filters["start_date"], filters["end_date"])
    if filters["payment_mode"]:
        qs = qs.filter(mode=filters["payment_mode"])
    data = (
        qs.values("payment_type__expense_group__name", "payment_type__name")
        .annotate(total=Sum("amount"))
        .order_by("payment_type__expense_group__name", "payment_type__name")
    )
    headers = ["Expense Group", "Expense Type", "Total Payments"]
    rows = [
        [
            row["payment_type__expense_group__name"] or "Unassigned",
            row["payment_type__name"] or "Unassigned",
            f'{row["total"] or 0:.2f}',
        ]
        for row in data
    ]
    return "Payments by Expense Group/Type", headers, rows


def report_courier_settlement(filters):
    sales_qs = models.SalesOrder.objects.filter(delivery_mode=models.DeliveryMode.COURIER)
    if filters["courier_partner_id"]:
        sales_qs = sales_qs.filter(courier_partner_id=filters["courier_partner_id"])
    sales_qs = _date_range(sales_qs, "sale__sale_date", filters["start_date"], filters["end_date"])
    fees = (
        sales_qs.values("courier_partner__id", "courier_partner__name")
        .annotate(fee_total=Sum("courier_fee"))
    )

    received_qs = models.DeliveryStatus.objects.select_related("sale__sales_order__courier_partner")
    if filters["courier_partner_id"]:
        received_qs = received_qs.filter(
            sale__sales_order__courier_partner_id=filters["courier_partner_id"]
        )
    received_qs = _date_range(received_qs, "received_date", filters["start_date"], filters["end_date"])
    received = (
        received_qs.values("sale__sales_order__courier_partner__id")
        .annotate(collected=Sum("received_amount"))
    )
    received_map = {r["sale__sales_order__courier_partner__id"]: r["collected"] or 0 for r in received}

    headers = ["Courier Partner", "Collected", "Courier Fees", "Net Settlement"]
    rows = []
    for row in fees:
        collected = received_map.get(row["courier_partner__id"], 0)
        fee_total = row["fee_total"] or 0
        rows.append([
            row["courier_partner__name"] or "Unassigned",
            f"{collected:.2f}",
            f"{fee_total:.2f}",
            f"{(collected - fee_total):.2f}",
        ])
    return "Courier Settlement Summary", headers, rows


def report_day_close(filters):
    qs = models.DayClose.objects.all()
    qs = _date_range(qs, "date", filters["start_date"], filters["end_date"])
    headers = [
        "Date",
        "Opening Cash",
        "Opening Bank",
        "Total Receipts",
        "Total Payments",
        "Closing Cash",
        "Closing Bank",
    ]
    rows = [
        [
            d.date,
            f"{d.opening_cash_balance:.2f}",
            f"{d.opening_bank_balance:.2f}",
            f"{d.total_receipts:.2f}",
            f"{d.total_payments:.2f}",
            f"{d.closing_cash_balance:.2f}",
            f"{d.closing_bank_balance:.2f}",
        ]
        for d in qs.order_by("date")
    ]
    return "Day Close Summary", headers, rows


def report_vat(filters):
    profile = models.BusinessProfile.objects.first()
    total_sales = models.Sale.objects.aggregate(total=Sum("total_amount"))["total"] or 0
    total_receipts = models.Receipt.objects.aggregate(total=Sum("amount"))["total"] or 0
    headers = ["Field", "Value"]
    rows = [
        ["Business Name", profile.business_name if profile else ""],
        ["VAT No", profile.vat_number if profile else ""],
        ["VAT Submission Date 1", profile.vat_submission_date_1 if profile else ""],
        ["VAT Submission Date 2", profile.vat_submission_date_2 if profile else ""],
        ["VAT Submission Date 3", profile.vat_submission_date_3 if profile else ""],
        ["VAT Submission Date 4", profile.vat_submission_date_4 if profile else ""],
        ["Total Sales", f"{total_sales:.2f}"],
        ["Total Receipts", f"{total_receipts:.2f}"],
    ]
    return "VAT Report", headers, rows


REPORTS = {
    "sales-summary": report_sales_summary,
    "sales-by-customer-group": report_sales_by_customer_group,
    "sales-by-customer": report_sales_by_customer,
    "sales-by-product": report_sales_by_product,
    "sales-by-courier": report_sales_by_courier,
    "outstanding-by-customer": report_outstanding_by_customer,
    "outstanding-by-customer-group": report_outstanding_by_customer_group,
    "receipts-by-mode": report_receipts_by_mode,
    "payments-by-expense": report_payments_by_expense,
    "courier-settlement": report_courier_settlement,
    "day-close": report_day_close,
    "vat-report": report_vat,
}

REPORT_LABELS = {
    "sales-summary": "Sales Summary",
    "sales-by-customer-group": "Sales by Customer Group",
    "sales-by-customer": "Sales by Customer",
    "sales-by-product": "Sales by Product",
    "sales-by-courier": "Sales by Courier Partner",
    "outstanding-by-customer": "Outstanding by Customer",
    "outstanding-by-customer-group": "Outstanding by Customer Group",
    "receipts-by-mode": "Receipts by Mode",
    "payments-by-expense": "Payments by Expense Group/Type",
    "courier-settlement": "Courier Settlement Summary",
    "day-close": "Day Close Summary",
    "vat-report": "VAT Report",
}
