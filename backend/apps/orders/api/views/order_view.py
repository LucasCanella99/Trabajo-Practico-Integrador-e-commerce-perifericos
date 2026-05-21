from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser  # <--  Para recibir archivos/imágenes
from django.db import transaction

from apps.carts.models import Cart
from apps.orders.models import Order, OrderItem
from apps.orders.api.serializers.order_serializer import OrderSerializer

class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    # Esto le avisa a Django REST Framework que este endpoint acepta formularios con imágenes (Multipart)
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    serializer_class = OrderSerializer

    # 1. GENERAR LA COMPRA SUBIENDO COMPROBANTE: POST /orders/checkout/
    @action(detail=False, methods=['post'])
    def checkout(self, request):
        user = request.user

        #Si el cliente no subió el archivo del comprobante, lo frena 
        if 'comprobante_pago' not in request.FILES:
            return Response(
                {'error': 'El comprobante de pago en formato imagen es obligatorio para procesar la compra.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Paso 1: Buscamos el carrito activo del usuario
            try:
                cart = Cart.objects.get(user=user, state=True)
            except Cart.DoesNotExist:
                return Response({'error': 'No tienes un carrito activo para comprar.'}, status=status.HTTP_404_NOT_FOUND)

            # Paso 2: Traemos los ítems activos adentro de ese carrito
            cart_items = cart.items.filter(state=True)
            if not cart_items.exists():
                return Response({'error': 'El carrito está vacío. Agrega productos antes de comprar.'}, status=status.HTTP_400_BAD_REQUEST)

            # Paso 3: Creamos la cabecera de la Orden inyectando la imagen que mandó el Front
            order = Order.objects.create(
                user=user, 
                total=0.00,
                comprobante_pago=request.FILES['comprobante_pago']  # <-- CAPTURA LA IMAGEN Y LA SUBE A media/comprobantes/
            )
            total_acumulado = 0

            # Paso 4: Recorremos los renglones del carrito 
            for item in cart_items:
                product = item.product

                # Control de Stock
                if product.stock < item.quantity:
                    return Response(
                        {'error': f'Stock insuficiente para {product.name}. Disponible: {product.stock}'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Restamos el stock físico del catálogo
                product.stock -= item.quantity
                product.save()

                # Creamos el renglón fijo clonando el precio
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price
                )

                # Sumamos al total general
                total_acumulado += product.price * item.quantity

            # Paso 5: Guardamos el total definitivo en el Padre
            order.total = total_acumulado
            order.save()

            # Paso 6: Apagamos el carrito viejo (Soft Delete / Archivado)
            cart.state = False
            cart.save()

        # Retornamos la orden creada serializada
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    # 2. HISTORIAL DE PEDIDOS DEL CLIENTE: GET /orders/my_orders/
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        # El cliente logueado pide ver SOLO sus compras
        orders = Order.objects.filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)