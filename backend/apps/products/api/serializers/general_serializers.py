from apps.products.models import MeasureUnit, ProductCategory, Indicador
from rest_framework import serializers

class MeasureUnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = MeasureUnit
        exclude= ('state','created_date','deleted_date','modified_date',) # se excluye porque se cambia cuando se desee eliminar de forma soft algun registro


class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        exclude= ('state','created_date','deleted_date','modified_date',) 

class IndicadorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Indicador
        exclude= ('state','created_date','deleted_date','modified_date',) 

