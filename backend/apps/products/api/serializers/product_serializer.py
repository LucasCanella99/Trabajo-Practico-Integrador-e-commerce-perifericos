from rest_framework import serializers
from apps.products.models import Product
from apps.products.api.serializers.general_serializers import MeasureUnitSerializer, ProductCategorySerializer


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude= ('state','created_date','deleted_date','modified_date',)        

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'name': instance.name,
            'description' : instance.description,
            'price': instance.price,
            'product_image': instance.product_image.url if instance.product_image else '', #SI O SI debe acceder al la url de la image sino el json no lo traduce y hay un error de unicode
            'measure_unit': instance.measure_unit.description,  #accedo a las instancias de unidad de medida y la categoria
            'product_category': instance.product_category.description,

        }