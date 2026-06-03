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
    
    # Definimos los parsers por defecto para los métodos estándar
    parser_classes = [JSONParser]

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        user = request.user
        try:
            cart = Cart.objects.get(user=user, state=True)
        except Cart.DoesNotExist:
            return Response({'error': 'No tienes un carrito activo.'}, status=status.HTTP_404_NOT_FOUND)

        cart_items = cart.items.filter(state=True)
        if not cart_items.exists():
            return Response({'error': 'El carrito está vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response({'error': f'Stock insuficiente para {item.product.name}.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = Order.objects.create(user=user, total=0.00)
            total_acumulado = 0
            for item in cart_items:
                product = item.product
                product.stock -= item.quantity
                product.save()
                OrderItem.objects.create(order=order, product=product, quantity=item.quantity, price=product.price)
                total_acumulado += product.price * item.quantity
            order.total = total_acumulado
            order.save()
            cart.items.filter(state=True).update(state=False)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Sobrescribimos parser_classes SOLO para este método, permitiendo archivos
    @action(detail=True, methods=['patch'], parser_classes=[MultiPartParser, FormParser])
    def subir_comprobante(self, request, pk=None):
        order = self.get_object()
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'status': 'ok'})
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        return Response(serializer.errors, status=400)