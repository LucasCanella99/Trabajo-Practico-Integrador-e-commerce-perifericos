from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:                                 # Importa la metaclase User
        model = User
        fields = '__all__'                               # Es lo que trae de la meta clase (atributos/metodos)
                                                # Es lo que excluye de la meta clase el exlude =                       

    def create(self, validated_data):
        user = User(**self.validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        updated_user= super().update(instance,validated_data)
        updated_user.set_password(validated_data['password'])
        updated_user.save()
        return updated_user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User

    def to_representation(self, instance): #to representation es la salida de datos que le devolvemos al front
        return {
            'id': instance['id'],
            'username': instance['username'],
            'email': instance['email'],
            'password': instance['password']
        }