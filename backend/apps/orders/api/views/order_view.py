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

        # Encapsulamos las ESCRITURAS en una transacción atómica por seguridad.
        # IMPORTANTE: el bloque 'with transaction.atomic()' solo hace rollback ante excepciones reales.
        # Un 'return Response(...)' NO dispara rollback, por eso las validaciones
        # se realizan ANTES de entrar al bloque, así nunca se escribe nada a medias.

        # Paso 1: Buscamos el carrito activo del usuario
        try:
            cart = Cart.objects.get(user=user, state=True)
        except Cart.DoesNotExist:
            return Response({'error': 'No tienes un carrito activo para comprar.'}, status=status.HTTP_404_NOT_FOUND)

        # Paso 2: Traemos los ítems activos que están adentro de ese carrito usando el related_name='items'
        cart_items = cart.items.filter(state=True)
        if not cart_items.exists():
            return Response({'error': 'El carrito está vacío. Agrega productos antes de comprar.'}, status=status.HTTP_400_BAD_REQUEST)

        # ── FASE 1: Validar TODO antes de tocar la base de datos ──
        # Recorremos todos los ítems primero para detectar cualquier problema de stock.
        # Si algo falla acá, el return ocurre antes del bloque atómico: nada se escribió todavía.
        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response(
                    {'error': f'Stock insuficiente para {item.product.name}. Disponible: {item.product.stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # ── FASE 2: Todo validado, recién ahora escribimos ──
        with transaction.atomic():

            # Paso 3: Creamos la cabecera de la Orden (en revisión por defecto)
            order = Order.objects.create(user=user, total=0.00)
            total_acumulado = 0

            # Paso 4: Recorremos los renglones del carrito
            for item in cart_items:
                product = item.product

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

            # Paso 6: Vaciamos los ítems del carrito (Soft Delete de los ítems).
            # CAMBIO: antes se archivaba el carrito entero (cart.state = False),
            # lo que impedía crear un nuevo carrito por el OneToOneField.
            # Ahora el carrito queda activo y vacío, listo para la próxima compra.
            cart.items.filter(state=True).update(state=False)

        # Al salir del bloque transaction, si todo salió OK, impacta en la DB
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    # 2. HISTORIAL DE PEDIDOS DEL CLIENTE: GET /orders/my_orders/
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        # El cliente logueado pide ver SOLO sus compras
        orders = Order.objects.filter(user=request.user)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)