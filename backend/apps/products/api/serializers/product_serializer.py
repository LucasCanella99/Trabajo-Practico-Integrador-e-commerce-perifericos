from rest_framework import serializers
from apps.products.models import Product
from apps.products.api.serializers.general_serializers import MeasureUnitSerializer, ProductCategorySerializer


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        exclude= ('state','created_date','deleted_date','modified_date',)        

    def to_representation(self, instance):
        # Esta es la base pública del bucket en Supabase
        base_url = "https://payvlfqrsbrihdsashzt.supabase.co/storage/v1/object/public/media/"
        
        # Obtenemos la ruta relativa del archivo guardado en el modelo
        # Si instance.product_image es 'products/prueba.webp', esto devuelve el path completo
        image_path = instance.product_image.name if instance.product_image else ''
        
        return {
            'id': instance.id,
            'name': instance.name,
            'description' : instance.description,
            'price': instance.price,
            # Construimos la URL pública concatenando
            'product_image': f"{base_url}{image_path}" if image_path else '',
            'measure_unit': instance.measure_unit.description,
            'product_category': instance.product_category.description,
            'stock': instance.stock, 
        }