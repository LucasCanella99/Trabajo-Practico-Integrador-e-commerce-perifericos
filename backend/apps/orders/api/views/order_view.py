from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.carts.models import Cart
from apps.orders.models import Order, OrderItem
from apps.orders.api.serializers.order_serializer import OrderSerializer

class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    # 1. GENERAR LA COMPRA: POST /orders/checkout/
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        user = request.user

        # Encapsulamos todo en una transacción atómica por seguridad 
        # (esto hace que ante cualquier inconveniente sea del usuario o la DB, cancela toda la compra y vuelve todo al inicio)
        with transaction.atomic():
            # Paso 1: Buscamos el carrito activo del usuario
            try:
                cart = Cart.objects.get(user=user, state=True)
            except Cart.DoesNotExist:
                return Response({'error': 'No tienes un carrito activo para comprar.'}, status=status.HTTP_404_NOT_FOUND)

            # Paso 2: Traemos los ítems activos que están adentro de ese carrito usando elrelated_name='items'
            cart_items = cart.items.filter(state=True)
            if not cart_items.exists():
                return Response({'error': 'El carrito está vacío. Agrega productos antes de comprar.'}, status=status.HTTP_400_BAD_REQUEST)

            # Paso 3: Creamos la cabecera de la Orden (en revisión por defecto)
            order = Order.objects.create(user=user, total=0.00)
            total_acumulado = 0

            # Paso 4: Recorremos los renglones del carrito
            for item in cart_items:
                product = item.product

                # Control de Stock 
                if product.stock < item.quantity:
                    # Al tirar un error acá adentro, el 'with transaction.atomic()' 
                    # cancela todo lo que se haya hecho antes en este método
                    return Response(
                        {'error': f'Stock insuficiente para {product.name}. Disponible: {product.stock}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Restamos el stock físico del producto en el catálogo
                product.stock -= item.quantity
                product.save()

                # CLAVE: Creamos el renglón fijo clonando el precio de este milisegundo
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price  # <--- Acá se congela el precio
                )

                # Sumamos al total general de la factura
                total_acumulado += product.price * item.quantity

            # Paso 5: Guardamos el total definitivo en el Padre
            order.total = total_acumulado
            order.save()

            # Paso 6: Apagamos el carrito viejo (Soft Delete / Archivado)
            cart.state = False
            cart.save()

        # Al salir del bloque transaction, si todo salió OK, impacta en la DB
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    # 2. HISTORIAL DE PEDIDOS: GET /orders/my_orders/
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        # Buscador (QuerySet): Traemos todas las órdenes de este usuario
        orders = Order.objects.filter(user=request.user)
        
        # Pasamos la lista completa de facturas por nuestros dos serializadores
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)