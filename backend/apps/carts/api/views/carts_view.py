from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from apps.carts.models import Cart, CartItem
from apps.carts.api.serializers.carts_serializer import CartSerializer
from apps.products.models import Product

class CartViewSet(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    # 1. VER EL CARRITO: GET /carts/my_cart/
    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        # Trae el carrito activo del usuario, si no existe lo crea de cero
        cart, _ = Cart.objects.get_or_create(user=request.user, state=True)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 2. AGREGAR O SUMAR: POST /carts/add_item/
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, state=True)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        # Validamos que el Front nos mande un ID de producto
        if not product_id:
            return Response({'error': 'Falta el product_id'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscamos si el producto existe en la base de datos
        try:
            product = Product.objects.get(id=product_id, state=True)
        except Product.DoesNotExist:
            return Response({'error': 'El producto no existe'}, status=status.HTTP_404_NOT_FOUND)

        # Validamos el stock 
        if product.stock < quantity:
            return Response({'error': f'Stock insuficiente. Máximo disponible: {product.stock}'}, status=status.HTTP_400_BAD_REQUEST)

        # Buscamos o creamos el renglón del ítem en el carrito
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'state': True}
        )

        # Si el ítem ya existía en el carrito, lógica de actualización
        if not created:
            if not cart_item.state:
                # Si estaba borrado lógicamente, lo reactivamos con la nueva cantidad
                cart_item.state = True
                cart_item.quantity = quantity
            else:
                # Si ya estaba activo, sumamos las cantidades
                new_quantity = cart_item.quantity + quantity
                if product.stock < new_quantity:
                    return Response({'error': f'No podés sumar esa cantidad. Stock máximo: {product.stock}'}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.quantity = new_quantity
            
            cart_item.save()

        # carrito completo 
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 3. BORRAR ÍTEM (SOFT DELETE): DELETE /carts/remove_item/
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user, state=True)
        product_id = request.data.get('product_id')

        try:
            # Buscamos el ítem que quieren dar de baja
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id, state=True)
            # En vez de destruirlo físicamente, aplicamos Soft Delete cambiando el estado
            cart_item.state = False
            cart_item.save()
            
            serializer = CartSerializer(cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'El producto no está en el carrito'}, status=status.HTTP_404_NOT_FOUND)