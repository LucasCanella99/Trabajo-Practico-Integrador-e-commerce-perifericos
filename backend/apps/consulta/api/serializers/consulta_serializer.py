from rest_framework import serializers
from apps.consulta.models import Consulta

class ConsultaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consulta
        fields = ['id', 'nombre', 'email', 'mensaje', 'creado_en']
        read_only_fields = ['id', 'creado_en']