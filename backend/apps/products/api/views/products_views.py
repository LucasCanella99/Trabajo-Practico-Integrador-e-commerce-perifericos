from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from apps.products.api.serializers.product_serializer import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    # Definimos el queryset base (solo activos)
    queryset = ProductSerializer.Meta.model.objects.filter(state=True)

    # El método para borrar (Soft Delete) ó borrado lógico.
    def destroy(self, request, pk=None):
        product = self.get_queryset().filter(id=pk).first()
        if product:
            product.state = False  # No borramos, desactivamos(Sigue existiendo en la db pero no es visible en el navegador)
            product.save()
            return Response({'message': 'Producto eliminado correctamente'}, status=status.HTTP_200_OK)
        return Response({'error': 'No existe el producto'}, status=status.HTTP_400_BAD_REQUEST)