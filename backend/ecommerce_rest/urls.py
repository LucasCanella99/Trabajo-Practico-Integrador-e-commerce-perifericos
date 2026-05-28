"""
URL configuration for ecommerce_rest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView, # Login, devuelve acceso y refrescado
    TokenRefreshView, # Recibe refrescado y devuelve el nuevo acceso
)

urlpatterns = [
    # Nativo
    path('admin/', admin.site.urls),
    # Autenticación 
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Apps hechas
    path('usuario/', include('apps.users.api.urls')),
    path('products/', include('apps.products.api.urls')),
    path('carts/',include('apps.carts.api.urls')),
    path('orders/', include('apps.orders.api.urls')),
    path('consulta/', include('apps.consulta.api.urls')),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')), #REcuperación de contraseña.
    # Endpoint de solicitud de cambio POST /password_reset/---> Envia el mail
    # Endpont de confirmacion de cambio POST /password_reset/confirm/ ----> Se cambia la contraseña en la DB
    path('assets/', include('apps.assets.api.urls')),
    # Endpoint para que carguen imagenes como logo y esas cosas en el front 
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)