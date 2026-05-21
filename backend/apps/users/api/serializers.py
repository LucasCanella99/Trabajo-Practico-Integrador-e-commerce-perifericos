from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Explicicitamos qué campos entran y salen. Sacamos is_superuser e is_staff de acá.
        fields = ['id', 'username', 'email', 'name', 'last_name', 'image', 'password']
        extra_kwargs = {
            # La contraseña solo se recibe para crear/editar, NUNCA se manda en los JSON de respuesta
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Usamos el manager nativo que ya encripta la contraseña de forma segura
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        # Si actualizan los datos y viene una contraseña nueva, la hasheamos correctamente
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        return user


