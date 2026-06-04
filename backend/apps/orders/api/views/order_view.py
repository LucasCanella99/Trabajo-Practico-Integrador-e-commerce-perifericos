# apps/orders/api/views/order_view.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from django.db import transaction

from apps.carts.models import Cart
from apps.orders.models import Order, OrderItem
from apps.orders.api.serializers.order_serializer import OrderSerializer

class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = OrderSerializer
    parser_classes     = [JSONParser]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        user = request.user
        required = ['shipping_name', 'shipping_last_name', 'shipping_email', 'shipping_address']
        missing  = [f for f in required if not request.data.get(f, '').strip()]
        if missing:
            return Response({'error': f'Faltan datos de envío: {", ".join(missing)}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=user, state=True)
        except Cart.DoesNotExist:
            return Response({'error': 'No tenés un carrito activo.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.items.filter(state=True).select_related('product')
        if not cart_items.exists():
            return Response({'error': 'Tu carrito está vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response({'error': f'Stock insuficiente para "{item.product.name}". Disponible: {item.product.stock}'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                total=0,
                shipping_name      = request.data['shipping_name'].strip(),
                shipping_last_name = request.data['shipping_last_name'].strip(),
                shipping_email     = request.data['shipping_email'].strip(),
                shipping_address   = request.data['shipping_address'].strip(),
                transfer_confirmed = bool(request.data.get('transfer_confirmed', False)),
                status='PENDIENTE',
            )

            total_acumulado = 0
            for item in cart_items:
                product = item.product
                product.stock -= item.quantity
                product.save(update_fields=['stock'])

                OrderItem.objects.create(
                    order    = order,
                    product  = product,
                    quantity = item.quantity,
                    price    = product.price,
                )
                total_acumulado += product.price * item.quantity

            order.total = total_acumulado
            Order.objects.filter(pk=order.pk).update(total=total_acumulado)
            cart_items.update(state=False)

        order.refresh_from_db()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        orders     = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def confirmar_transferencia(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Orden no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'PENDIENTE':
            return Response({'error': f'No podés modificar una orden en estado "{order.get_status_display()}".'}, status=status.HTTP_400_BAD_REQUEST)

        order.transfer_confirmed = True
        order.save(update_fields=['transfer_confirmed', 'updated_at'])
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def cancelar(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Orden no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if order.status != 'PENDIENTE':
            return Response({'error': f'No podés cancelar una orden en estado "{order.get_status_display()}". Solo mientras está pendiente.'}, status=status.HTTP_400_BAD_REQUEST)

        motivo = request.data.get('cancel_reason', '').strip()
        if not motivo:
            return Response({'error': 'Indicá el motivo de cancelación.'}, status=status.HTTP_400_BAD_REQUEST)

        order.cancel_reason = motivo
        order.status        = 'CANCELADO'
        order.save()  # Ejecuta el rollback automático de stock que armamos en el modelo
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)