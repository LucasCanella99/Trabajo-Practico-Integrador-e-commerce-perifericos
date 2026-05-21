from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from apps.consulta.models import Consulta
from apps.consulta.api.serializers.consulta_serializer import ConsultaSerializer

# mixins.CreateModelMixin solo le habilita el POST al endpoint
class ConsultaViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Consulta.objects.all()
    serializer_class = ConsultaSerializer
    permission_classes = []  # Público, pero protegido por el rate limit de 1/min

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # Valida que el email sea real y que los campos no estén vacíos
        serializer.is_valid(raise_exception=True)
        # Guarda en la base de datos
        serializer.save()
        
        # Devolvemos la respuesta simple que vos querías
        return Response(
            {"mensaje": "Consulta recibida correctamente. Nos pondremos en contacto pronto!"}, 
            status=status.HTTP_201_CREATED
        )