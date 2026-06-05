from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from apps.products.api.serializers.product_serializer import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    queryset = ProductSerializer.Meta.model.objects.filter(state=True)
    
    #Motores de búsqueda y filtrado de DRF
    filter_backends = [SearchFilter]
    
    #Que campos va a buscar cuando el Front mande ?search=
    search_fields = ['name', 'description']

    # Sobreescribimos el list para meterle un filtro rápido por categoría si viene en la URL
    def get_queryset(self):
        queryset = super().get_queryset()
        # Capturamos si el Front manda algo como ?categoria=1
        category_id = self.request.query_params.get('categoria', None)
        if category_id is not None:
            queryset = queryset.filter(product_category_id=category_id)
        return queryset


    def destroy(self, request, pk=None):
        product = self.get_queryset().filter(id=pk).first()
        if product:
            product.delete_logical()
            return Response({'message': 'Producto eliminado correctamente'}, status=status.HTTP_200_OK)
        return Response({'error': 'No existe el producto'}, status=status.HTTP_400_BAD_REQUEST)
