from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.carts.api.views.carts_view import CartViewSet

# El DefaultRouter  arma automático las rutas para las @action  (my_cart, add_item, remove_item)
router = DefaultRouter()
router.register(r'', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]