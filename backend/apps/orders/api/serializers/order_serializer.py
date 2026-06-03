from rest_framework import serializers
from apps.orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    username = serializers.ReadOnlyField(source='user.username')
    client_name = serializers.ReadOnlyField(source='user.name')   
    client_email = serializers.ReadOnlyField(source='user.email') 

    class Meta:
        model = Order
        fields = [
            'id', 'username', 'client_name', 'client_email', 
            'created_at', 'total', 'status', 'status_display', 
            'comprobante_pago', 'items'
        ]
        
        # IMPORTANTE: 
        # Aquí 'comprobante_pago' NO está en read_only_fields.
        # Esto permite que el PATCH lo pueda modificar.
        read_only_fields = [
            'id', 'username', 'client_name', 'client_email', 
            'created_at', 'total', 'status', 'status_display', 'items'
        ]