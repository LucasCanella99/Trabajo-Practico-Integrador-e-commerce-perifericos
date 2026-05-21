from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.consulta.api.views.consulta_view import ConsultaViewSet

# El router mapea automáticamente el método POST de tu ViewSet a la URL raíz
router = DefaultRouter()
router.register(r'', ConsultaViewSet, basename='consulta')

urlpatterns = [
    path('', include(router.urls)),
]