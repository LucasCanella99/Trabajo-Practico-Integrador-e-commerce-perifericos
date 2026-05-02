from django.urls import path
from apps.users.api.api import user_api_view, user_detail_api_view

urlpatterns = [
    path('', user_api_view, name = 'usuario_api'), # as_view disfraza la clase serializadora de funcion para que django pueda procesarla
    path('<int:pk>/',user_detail_api_view,name ='usuario_detail_api_view') # S-Cambio: Eliminé redundancia (doble endpoint /usuario)
]
