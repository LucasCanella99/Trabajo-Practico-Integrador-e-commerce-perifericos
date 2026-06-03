from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db import transaction

from apps.carts.models import Cart
from apps.orders.models import Order, OrderItem
from apps.orders.api.serializers.order_serializer import OrderSerializer

class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    parser_classes = [JSONParser]  # Por defecto para JSON

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """Paso 1: Crear la orden sin comprobante"""
        user = request.user

        # Obtener o crear carrito activo
        cart, _ = Cart.objects.get_or_create(user=user, defaults={'state': True})
        if not cart.state:
            cart.state = True
            cart.save()

        cart_items = cart.items.filter(state=True)
        if not cart_items.exists():
            return Response(
                {'error': 'El carrito está vacío. Agregá productos antes de comprar.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar stock
        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response(
                    {'error': f'Stock insuficiente para {item.product.name}. Disponible: {item.product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Crear la orden en una transacción
        with transaction.atomic():
            order = Order.objects.create(user=user, total=0)
            total_acumulado = 0

            for item in cart_items:
                product = item.product
                product.stock -= item.quantity
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price
                )
                total_acumulado += product.price * item.quantity

            order.total = total_acumulado
            order.save()

            # Vaciar carrito (soft delete)
            cart_items.update(state=False)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Listar órdenes del usuario"""
        orders = Order.objects.filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], parser_classes=[MultiPartParser, FormParser])
    def subir_comprobante(self, request, pk=None):
        """Paso 2: Subir comprobante a una orden existente"""
        try:
            order = self.get_object()
        except Order.DoesNotExist:
            return Response({'error': 'Orden no encontrada'}, status=status.HTTP_404_NOT_FOUND)

        if 'comprobante_pago' not in request.FILES:
            return Response({'error': 'No se envió ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

        order.comprobante_pago = request.FILES['comprobante_pago']
        order.save()

        return Response({
            'status': 'ok',
            'message': 'Comprobante subido correctamente',
            'comprobante_url': order.comprobante_pago.url if order.comprobante_pago else None
        }, status=status.HTTP_200_OK)