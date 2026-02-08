from rest_framework import serializers
from . import models


class BusinessProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BusinessProfile
        fields = "__all__"


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tax
        fields = "__all__"


class CustomerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomerGroup
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Supplier
        fields = "__all__"


class CourierPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourierPartner
        fields = "__all__"


class ExpenseGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExpenseGroup
        fields = "__all__"


class ExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExpenseType
        fields = "__all__"


class ReceiptTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReceiptType
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = "__all__"


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Unit
        fields = "__all__"


class ProductUnitPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductUnitPrice
        fields = "__all__"


class SalesOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SalesOrderItem
        fields = "__all__"


class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.SalesOrder
        fields = "__all__"


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sale
        fields = "__all__"


class DeliveryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliveryStatus
        fields = "__all__"


class ReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Receipt
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Payment
        fields = "__all__"


class DayCloseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DayClose
        fields = "__all__"


class ProductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Production
        fields = "__all__"


class PurchaseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PurchaseItem
        fields = "__all__"


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.Purchase
        fields = "__all__"
