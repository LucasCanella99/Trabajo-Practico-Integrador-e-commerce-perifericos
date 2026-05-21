from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.users.models import User
from apps.users.api.serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        # Permitimos que cualquiera entre al POST para registrarse sin token
        if self.action == 'create':
            return [AllowAny()]
        # Para ver la lista, editar o borrar, que herede los permisos globales del sistema
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.pop('is_superuser', None)
        data.pop('is_staff', None)
        data.pop('is_active', None)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"message": "¡Usuario registrado con éxito!"}, 
            status=status.HTTP_201_CREATED
        )