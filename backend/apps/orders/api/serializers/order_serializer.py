from rest_framework import serializers
from apps.orders.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    # Usamos un ReadOnlyField para traer directo el nombre del producto desde la relación
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    # Renglones de la orden asociados (muchos ítems)
    items = OrderItemSerializer(many=True, read_only=True)
    
    # Mapeo automático para devolver el texto descriptivo del estado (ej: 'Pendiente de aprobación')
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Datos del cliente extraídos directo de la relación con el usuario logueado
    username = serializers.ReadOnlyField(source='user.username')
    client_name = serializers.ReadOnlyField(source='user.name')   
    client_email = serializers.ReadOnlyField(source='user.email') 

    class Meta:
        model = Order
        # Agregamos los nuevos campos y 'comprobante_pago' para que viaje la URL de la imagen
        fields = [
            'id', 
            'username', 
            'client_name', 
            'client_email', 
            'created_at', 
            'total', 
            'status', 
            'status_display', 
            'comprobante_pago',  
            'items'
        ]
        # Nos aseguramos de que el total y el estado no puedan ser manipulados por el Front
        read_only_fields = ['total', 'status']