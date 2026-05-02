from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from apps.users.api.serializers import UserSerializer, UserListSerializer
from apps.users.models import User


@api_view(['GET','POST'])
def user_api_view(request): # El request es lo que pide el navegador al backend
    #list
    if request.method == 'GET':
        users = User.objects.all().values('id','username','email','password') # Agarra todos los objetos del modelo usuario
        users_serializer = UserListSerializer(users,many = True) # Los serieliza todos en JSON
        
        return Response(users_serializer.data, status= status.HTTP_200_OK) # Aca se hace el retorno del Json, los datos serializados del User / tiene que devolver un código HTTP de estado el response siempre
    #create
    elif request.method == 'POST':
        users_serializer = UserSerializer(data = request.data) # aca "deserializa" la informacion del nav y la convierte en un objeto y compara atributos
        #validation
        if users_serializer.is_valid(): # Válida la info
            users_serializer.save() # Si la clase(Model) Usuario no tiene un save encriptado, guarda el que es por defecto que es una cagada. No lo encripta
            return Response({'message': 'Usuario creado correctamente!'}, status = status.HTTP_201_CREATED)
        return Response(users_serializer.errors, status= status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','PUT','DELETE'])
def user_detail_api_view(request,pk= None): # Acá pide que aparte de la petición GET venga con una primare key para filtrar los usuarios registrados por su id
    #queryset
    user = User.objects.filter(id = pk).first() # El filtro devuelve una queryset si esta vacia da un none como first object y sino devuelve la instancia de usuario buscada por us id
    #validacion
    if user: #si usuario es True, que no es none, ejecuta todo lo que viene despues
        #retrieve
        if request.method == 'GET':
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status= status.HTTP_200_OK)    
        #update
        elif request.method == 'PUT':
            user_serializer = UserSerializer(user, data=request.data) # Serializa al objeto usuario(y corrobora que no sea un post) y hace que la data de la request sea esta nueva data serializada que valida, guarda y reenvia 
            if user_serializer.is_valid():
                user_serializer.save()
                return Response(user_serializer.data, status= status.HTTP_200_OK)
            return Response(user_serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        #delete
        elif request.method == 'DELETE':
            user.delete()
            return Response({'message': 'Usuario eliminado correctamente!'}, status= status.HTTP_200_OK) # S-Cambio: era 204_OK (no existe), acá podría usarse 204_NO_CONTENT o 200_OK, pero el único que admite un mensaje es 200, 204 no acepta un body por HTTP spec

    return Response({'message':'No se ha encontrado un usuario con estos datos'}, status= status.HTTP_404_NOT_FOUND) # Caso usuario no encontrado con la pk
