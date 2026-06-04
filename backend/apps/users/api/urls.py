# apps/users/api/urls.py
from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.users.api.api import UserViewSet

router = DefaultRouter()
router.register('', UserViewSet, basename='usuarios')

urlpatterns = router.urls
