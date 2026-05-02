from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:                                 # Importa la metaclase User
        model = User
        fields = '__all__'                      # Es lo que trae de la meta clase (atributos/metodos)
        # S-Nota: voy a dejar fields en all por pragmatismo, pero habría que ser explicitos con lo que entra, porque probé haciendo un PUT en un usuario poniendo "is_superuser": true y lo hice admin, eso es una vulnerabilidad de seguridad fea, cuando entreguemos esto hay que explicitar los campos que toma, sea usando la variable exclude o especificando en fields.
        extra_kwargs = {
                'password': {'write_only': True} # S-Cambio: acepta password como input pero nunca lo devuelve, más robusto
        }                                                                      

    def create(self, validated_data):
        user = User(**validated_data) # S-Cambio: era self.validated_data, pero el parámetro ya lo trae, no hace falta el self 
        user.set_password(validated_data['password'])
        user.save()
        return user

# S-Cambio: antes updated_user guardaba todo y posteriormente hasheaba password, si llegara a haber cualquier proceso que lea la tabla en ese tiempo previo al hasheado quedaría expuesto password
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)  
        updated_user = super().update(instance, validated_data)
        # Hasta acá guarda todo menos password 
        
        if password:
            updated_user.set_password(password) # hasheo
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
