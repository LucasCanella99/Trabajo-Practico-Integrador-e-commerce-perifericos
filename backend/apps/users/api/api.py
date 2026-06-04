# apps/users/api/api.py
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
import secrets
from django.core.cache import cache
from django.contrib.auth import get_user_model

from apps.users.models import User, SecurityQuestion
from apps.users.api.serializers import UserSerializer, UserRegisterSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset         = User.objects.filter(is_active=True)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'user_register':
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

    # --------------------------------------------------------------
    # NUEVAS ACCIONES PARA QUE FUNCIONE EL FRONTEND ACTUAL
    # --------------------------------------------------------------

    @action(detail=False, methods=['post'], url_path='register')
    def user_register(self, request):
        """
        Registro con preguntas de seguridad fijas.
        Endpoint: POST /users/register/
        Espera: username, email, name, last_name, password, security_questions (lista)
        """
        data = request.data.copy()
        data.pop('is_superuser', None)
        data.pop('is_staff', None)
        data.pop('is_active', None)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Usuario registrado con éxito", "id": user.id}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='verify_security_answers')
    def verify_security_answers(self, request):
        """
        Verifica las respuestas de seguridad para un username.
        Endpoint: POST /users/verify_security_answers/
        Espera: { "username": "ejemplo", "respuestas": [{"question": "¿Nombre de tu primera mascota?", "answer": "..."}, ...] }
        """
        username = request.data.get('username')
        respuestas = request.data.get('respuestas', [])

        if not username or len(respuestas) != 3:
            return Response({'error': 'Faltan datos o cantidad de respuestas incorrecta.'}, status=400)

        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        # Verificar cada respuesta
        for ans in respuestas:
            question_text = ans.get('question')
            answer_text = ans.get('answer', '').strip().lower()
            try:
                sq = SecurityQuestion.objects.get(user=user, question=question_text)
                if not sq.check_answer(answer_text):
                    return Response({'error': f'Respuesta incorrecta para: {question_text}'}, status=400)
            except SecurityQuestion.DoesNotExist:
                return Response({'error': f'Pregunta no registrada: {question_text}'}, status=400)

        return Response({'message': 'Respuestas correctas'})

    @action(detail=False, methods=['post'], url_path='change_password')
    def change_password(self, request):
        """
        Cambia la contraseña de un usuario (sin token, solo username + nueva contraseña).
        Endpoint: POST /users/change_password/
        Espera: { "username": "ejemplo", "new_password": "nueva_contraseña" }
        """
        username = request.data.get('username')
        new_password = request.data.get('new_password')

        if not username or not new_password:
            return Response({'error': 'Usuario y nueva contraseña son requeridos.'}, status=400)

        if len(new_password) < 8:
            return Response({'error': 'La contraseña debe tener al menos 8 caracteres.'}, status=400)

        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=404)

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Contraseña actualizada correctamente.'})


# ============================================================
# CLASES EXISTENTES (para compatibilidad con otro flujo, si las usas)
# ============================================================

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
        cache.set(cache_key, user.pk, timeout=600)

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