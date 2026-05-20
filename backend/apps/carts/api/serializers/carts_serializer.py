from rest_framework import serializers
from apps.carts.models import Cart, CartItem
from apps.products.api.serializers.product_serializer import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'state']

    def to_representation(self, instance):
        # Usamos ProductSerializer para renderizar toda la info limpia del producto
        product_data = ProductSerializer(instance.product).data

        return {
            'id': instance.id,
            'quantity': instance.quantity,
            # Multiplicamos la cantidad por el precio que ya viene del producto
            'subtotal': instance.quantity * instance.product.price,
            'state': instance.state,
            'product': product_data  # Acá adentro viaja el JSON con la imagen, unidad de medida, etc.
        }

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'state']

    def to_representation(self, instance):
        # Filtramos solo los ítems activos (state=True) usando el related_name='items'
        active_items = instance.items.filter(state=True)
        
        # Serializamos esa lista de ítems usando el serializador de arriba
        items_data = CartItemSerializer(active_items, many=True).data

        # Calculamos los totales recorriendo los ítems activos
        total_price = sum(item.quantity * item.product.price for item in active_items)
        total_items = sum(item.quantity for item in active_items)

        return {
            'id': instance.id,
            'user': instance.user.id,
            'username': instance.user.username,  # Para el Front así saludan al usuario
            'total_price': total_price,
            'total_items': total_items,
            'state': instance.state,
            'items': items_data  # La lista con todos los productos adentro
        }