# apps/users/api/api.py
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import secrets
from django.core.cache import cache

from apps.users.models import User, SecurityQuestion
from apps.users.api.serializers import UserSerializer, UserRegisterSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data.pop('is_superuser', None)
        data.pop('is_staff', None)
        data.pop('is_active', None)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "¡Usuario registrado con éxito!"}, status=status.HTTP_201_CREATED)

class ObtenerPreguntasSeguridad(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response({'error': 'Ingresá tu email.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'No encontramos una cuenta con ese email.'}, status=status.HTTP_404_NOT_FOUND)

        preguntas = SecurityQuestion.objects.filter(user=user)
        if preguntas.count() != 3:
            return Response({'error': 'Esta cuenta no tiene preguntas de seguridad configuradas.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'user_id': user.id,
            'preguntas': [{'id': p.id, 'question': p.question, 'question_display': p.get_question_display()} for p in preguntas]
        }, status=status.HTTP_200_OK)

class VerificarRespuestas(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id   = request.data.get('user_id')
        respuestas = request.data.get('respuestas', [])

        if not user_id or len(respuestas) != 3:
            return Response({'error': 'Datos incompletos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        errores = 0
        for r in respuestas:
            pregunta_id = r.get('id')
            answer_raw  = r.get('answer', '')
            try:
                pregunta = SecurityQuestion.objects.get(pk=pregunta_id, user=user)
                if not pregunta.check_answer(answer_raw):
                    errores += 1
            except SecurityQuestion.DoesNotExist:
                errores += 1

        if errores > 0:
            return Response({'error': 'Una o más respuestas son incorrectas. Intentá de nuevo.'}, status=status.HTTP_400_BAD_REQUEST)

        token = secrets.token_urlsafe(32)
        cache_key = f"pw_reset_{token}"
        cache.set(cache_key, user.pk, timeout=600)  # Vence en 10 minutos

        return Response({'reset_token': token}, status=status.HTTP_200_OK)

class CambiarContrasenaConToken(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token        = request.data.get('reset_token', '').strip()
        new_password = request.data.get('new_password', '').strip()

        if not token or not new_password:
            return Response({'error': 'Faltan datos.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 8:
            return Response({'error': 'La contraseña debe tener al menos 8 caracteres.'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"pw_reset_{token}"
        user_pk   = cache.get(cache_key)

        if not user_pk:
            return Response({'error': 'El token expiró o ya fue usado. Reiniciá el proceso.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_pk, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        cache.delete(cache_key)

        return Response({'message': 'Contraseña actualizada correctamente. Ya podés iniciar sesión.'}, status=status.HTTP_200_OK)