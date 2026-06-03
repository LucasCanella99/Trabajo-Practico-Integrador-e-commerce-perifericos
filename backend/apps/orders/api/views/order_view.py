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
    parser_classes = [JSONParser]

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def checkout(self, request):
        user = request.user
        
        # Intentar obtener el carrito activo
        try:
            cart = Cart.objects.get(user=user, state=True)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'No tenés un carrito activo. Agregá productos primero.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = cart.items.filter(state=True)
        
        if not cart_items.exists():
            return Response(
                {'error': 'El carrito está vacío'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar stock
        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response(
                    {'error': f'Stock insuficiente para {item.product.name}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Crear orden
        with transaction.atomic():
            order = Order.objects.create(user=user, total=0)
            total = 0
            
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
                total += product.price * item.quantity
            
            order.total = total
            order.save()
            
            # Marcar items del carrito como inactivos
            cart_items.update(state=False)
            
            # Si viene un comprobante en la request, guardarlo
            if 'comprobante_pago' in request.FILES:
                order.comprobante_pago = request.FILES['comprobante_pago']
                order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['patch'], parser_classes=[MultiPartParser, FormParser])
    def subir_comprobante(self, request, pk=None):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Orden no encontrada'}, status=404)
        
        if 'comprobante_pago' not in request.FILES:
            return Response({'error': 'No se envió ningún archivo'}, status=400)
        
        order.comprobante_pago = request.FILES['comprobante_pago']
        order.save()
        
        return Response({'status': 'ok', 'message': 'Comprobante subido'})