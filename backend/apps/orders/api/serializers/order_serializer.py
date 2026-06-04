# apps/orders/api/serializers/order_serializer.py
from rest_framework import serializers
from apps.orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model  = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items          = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    username       = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model  = Order
        fields = [
            'id', 'username',
            'shipping_name', 'shipping_last_name', 'shipping_email', 'shipping_address',
            'total', 'status', 'status_display', 'transfer_confirmed', 'cancel_reason',
            'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'username', 'total', 'status', 'status_display',
            'items', 'created_at', 'updated_at',
        ]