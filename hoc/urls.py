"""hoc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hoc.admin_site import admin_site
from core import api as core_api
from core import report_views
from core import views as core_views

router = DefaultRouter()
router.register("business-profiles", core_api.BusinessProfileViewSet)
router.register("taxes", core_api.TaxViewSet)
router.register("customer-groups", core_api.CustomerGroupViewSet)
router.register("customers", core_api.CustomerViewSet)
router.register("suppliers", core_api.SupplierViewSet)
router.register("courier-partners", core_api.CourierPartnerViewSet)
router.register("expense-groups", core_api.ExpenseGroupViewSet)
router.register("expense-types", core_api.ExpenseTypeViewSet)
router.register("receipt-types", core_api.ReceiptTypeViewSet)
router.register("products", core_api.ProductViewSet)
router.register("units", core_api.UnitViewSet)
router.register("product-unit-prices", core_api.ProductUnitPriceViewSet)
router.register("sales-orders", core_api.SalesOrderViewSet)
router.register("sales-order-items", core_api.SalesOrderItemViewSet)
router.register("sales", core_api.SaleViewSet)
router.register("delivery-status", core_api.DeliveryStatusViewSet)
router.register("receipts", core_api.ReceiptViewSet)
router.register("payments", core_api.PaymentViewSet)
router.register("day-close", core_api.DayCloseViewSet)
router.register("productions", core_api.ProductionViewSet)
router.register("purchases", core_api.PurchaseViewSet)
router.register("purchase-items", core_api.PurchaseItemViewSet)

urlpatterns = [
    path("", core_views.dashboard, name="dashboard"),
    path("backend/", core_views.backend_home, name="backend_home"),
    path("backend/products/", core_views.backend_module_list, {"module_slug": "products"}, name="backend_products"),
    path("backend/production/", core_views.backend_module_list, {"module_slug": "production"}, name="backend_production"),
    path("backend/purchases/", core_views.backend_module_list, {"module_slug": "purchases"}, name="backend_purchases"),
    path("backend/modules/<slug:module_slug>/", core_views.backend_module_list, name="backend_module_list"),
    path("backend/modules/<slug:module_slug>/add/", core_views.backend_module_create, name="backend_module_create"),
    path("backend/modules/<slug:module_slug>/<int:pk>/edit/", core_views.backend_module_edit, name="backend_module_edit"),
    path("backend/modules/<slug:module_slug>/<int:pk>/delete/", core_views.backend_module_delete, name="backend_module_delete"),
    path("admin/", admin_site.urls),
    path("reports/", report_views.reports_index, name="reports_index"),
    path("reports/<slug:slug>/", report_views.report_view, name="report_view"),
    path("reports/<slug:slug>/export/<str:fmt>/", report_views.report_export, name="report_export"),
    path("api/", include(router.urls)),
]
