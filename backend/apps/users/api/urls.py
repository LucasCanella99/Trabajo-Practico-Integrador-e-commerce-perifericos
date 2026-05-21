from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.users.api.api import UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='usuarios')

urlpatterns = [
    path('', include(router.urls)),
]

