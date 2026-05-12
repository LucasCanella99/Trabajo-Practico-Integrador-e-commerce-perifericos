from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.products.api.views.general_views import MeasureUnitListAPIVIEW, IndicadorListAPIVIEW, ProductCategoryListAPIVIEW

from apps.products.api.views.products_views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [

    path('measure_unit/', MeasureUnitListAPIVIEW.as_view(), name='measure_unit'),
    path('indicador/', IndicadorListAPIVIEW.as_view(), name='indicador'),
    path('product_category/', ProductCategoryListAPIVIEW.as_view(), name='product_category'),
    

    path('', include(router.urls)),
]