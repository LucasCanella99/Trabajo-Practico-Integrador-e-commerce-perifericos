from django.contrib import admin
from apps.products.models import *
# Register your models here.
# Estas dos clases son para que en el panel de admin de django aparezcan las dos cosas id y description
class MeasureUnitAdmin(admin.ModelAdmin):
    list_display=('id','description')

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display=('id','description')

admin.site.register(MeasureUnit,MeasureUnitAdmin)
admin.site.register(ProductCategory,ProductCategoryAdmin)
admin.site.register(Indicador)
admin.site.register(Product)