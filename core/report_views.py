from io import BytesIO

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render

from . import models
from .reports import REPORT_LABELS, REPORTS, get_filters
from .views import MODULE_GROUPS


def _excel_response(title, headers, rows):
    try:
        from openpyxl import Workbook
    except Exception:
        return HttpResponseBadRequest("openpyxl is not installed.")

    wb = Workbook()
    ws = wb.active
    ws.title = title[:31]
    ws.append(headers)
    for row in rows:
        ws.append(row)

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{title}.xlsx"'
    return response


def _pdf_response(title, headers, rows):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
    except Exception:
        return HttpResponseBadRequest("reportlab is not installed.")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph(title, styles["Heading1"]), Spacer(1, 12)]
    table_data = [headers] + rows
    table = Table(table_data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{title}.pdf"'
    return response


@staff_member_required
def reports_index(request):
    return redirect("report_view", slug="sales-summary")


@staff_member_required
def report_view(request, slug):
    report_fn = REPORTS.get(slug)
    if not report_fn:
        return HttpResponseBadRequest("Unknown report.")

    filters = get_filters(request.GET)
    title, headers, rows = report_fn(filters)

    context = {
        "title": title,
        "headers": headers,
        "rows": rows,
        "slug": slug,
        "reports": list(REPORT_LABELS.items()),
        "selected_report_name": REPORT_LABELS.get(slug, slug.replace("-", " ").title()),
        "filters": filters,
        "customers": models.Customer.objects.all(),
        "customer_groups": models.CustomerGroup.objects.all(),
        "courier_partners": models.CourierPartner.objects.all(),
        "products": models.Product.objects.all(),
        "order_types": models.OrderType.choices,
        "payment_modes": models.PaymentMode.choices,
        "module_groups": MODULE_GROUPS,
    }
    return render(request, "reports/report.html", context)


@staff_member_required
def report_export(request, slug, fmt):
    report_fn = REPORTS.get(slug)
    if not report_fn:
        return HttpResponseBadRequest("Unknown report.")

    filters = get_filters(request.GET)
    title, headers, rows = report_fn(filters)
    safe_title = slug.replace("-", "_")

    if fmt == "excel":
        return _excel_response(safe_title, headers, rows)
    if fmt == "pdf":
        return _pdf_response(safe_title, headers, rows)
    return HttpResponseBadRequest("Unknown export format.")
