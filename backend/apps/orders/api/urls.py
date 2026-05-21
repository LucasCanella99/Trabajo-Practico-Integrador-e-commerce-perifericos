from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.api.views.order_view import OrderViewSet

# El router se encarga de mapear los métodos del ViewSet a URLs reales
router = DefaultRouter()
router.register(r'', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router.urls)),
]