from rest_framework import viewsets
from . import models, serializers


class BusinessProfileViewSet(viewsets.ModelViewSet):
    queryset = models.BusinessProfile.objects.all()
    serializer_class = serializers.BusinessProfileSerializer


class TaxViewSet(viewsets.ModelViewSet):
    queryset = models.Tax.objects.all()
    serializer_class = serializers.TaxSerializer


class CustomerGroupViewSet(viewsets.ModelViewSet):
    queryset = models.CustomerGroup.objects.all()
    serializer_class = serializers.CustomerGroupSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = models.Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer


class CourierPartnerViewSet(viewsets.ModelViewSet):
    queryset = models.CourierPartner.objects.all()
    serializer_class = serializers.CourierPartnerSerializer


class ExpenseGroupViewSet(viewsets.ModelViewSet):
    queryset = models.ExpenseGroup.objects.all()
    serializer_class = serializers.ExpenseGroupSerializer


class ExpenseTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ExpenseType.objects.all()
    serializer_class = serializers.ExpenseTypeSerializer


class ReceiptTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ReceiptType.objects.all()
    serializer_class = serializers.ReceiptTypeSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = models.Unit.objects.all()
    serializer_class = serializers.UnitSerializer


class ProductUnitPriceViewSet(viewsets.ModelViewSet):
    queryset = models.ProductUnitPrice.objects.all()
    serializer_class = serializers.ProductUnitPriceSerializer


class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = models.SalesOrder.objects.all()
    serializer_class = serializers.SalesOrderSerializer


class SalesOrderItemViewSet(viewsets.ModelViewSet):
    queryset = models.SalesOrderItem.objects.all()
    serializer_class = serializers.SalesOrderItemSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = models.Sale.objects.all()
    serializer_class = serializers.SaleSerializer


class DeliveryStatusViewSet(viewsets.ModelViewSet):
    queryset = models.DeliveryStatus.objects.all()
    serializer_class = serializers.DeliveryStatusSerializer


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = models.Receipt.objects.all()
    serializer_class = serializers.ReceiptSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = models.Payment.objects.all()
    serializer_class = serializers.PaymentSerializer


class DayCloseViewSet(viewsets.ModelViewSet):
    queryset = models.DayClose.objects.all()
    serializer_class = serializers.DayCloseSerializer


class ProductionViewSet(viewsets.ModelViewSet):
    queryset = models.Production.objects.all()
    serializer_class = serializers.ProductionSerializer


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = models.Purchase.objects.all()
    serializer_class = serializers.PurchaseSerializer


class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = models.PurchaseItem.objects.all()
    serializer_class = serializers.PurchaseItemSerializer
