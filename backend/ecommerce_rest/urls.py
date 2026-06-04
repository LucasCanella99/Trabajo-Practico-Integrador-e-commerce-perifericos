# ecommerce_rest/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.api.api import (
    ObtenerPreguntasSeguridad,
    VerificarRespuestas,
    CambiarContrasenaConToken,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth Básica
    path('auth/login/',   TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(),    name='token_refresh'),

    # Recuperación limpia por preguntas (Caché local)
    path('auth/recuperar/preguntas/', ObtenerPreguntasSeguridad.as_view(), name='recuperar_preguntas'),
    path('auth/recuperar/verificar/', VerificarRespuestas.as_view(),       name='recuperar_verificar'),
    path('auth/recuperar/cambiar/',   CambiarContrasenaConToken.as_view(), name='recuperar_cambiar'),

    # Modulos de la App
    path('usuario/',  include('apps.users.api.urls')),
    path('products/', include('apps.products.api.urls')),
    path('carts/',    include('apps.carts.api.urls')),
    path('orders/',   include('apps.orders.api.urls')),
    path('consulta/', include('apps.consulta.api.urls')),
    path('assets/',   include('apps.assets.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)