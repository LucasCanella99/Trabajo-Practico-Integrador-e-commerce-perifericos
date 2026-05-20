from django.db import models
from simple_history.models import HistoricalRecords
from apps.base.models import BaseModel

# Create your models here

# Esta clase es para tener las unidades de medida al realizar la compra es obligatorio y tambien registra todo el hsitorial de creacion mod o eliminacion porque hereda de BaseModel
class MeasureUnit(BaseModel):
    #campo obligarorio 
    description= models.CharField('Description', max_length= 50,blank= False, null= False, unique= True)
    historical = HistoricalRecords() #Tabla espejo, es el historial de cambios

    @property
    def _history_user(self):
        return self.changed_by
    
    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    
    class Meta:

        verbose_name = 'Unidad de Medida'
        verbose_name_plural = 'Unidades de Medidas'
    
    def __str__(self):
        return self.description

#Esta clase es la que define la categoria de los productos, obviamente guardando el historial de modificaciones. Esta directamente "conectada" a la tabla de base de datos de una unidad de medida gracias a ForeignKey, que esta misma la relaciona a una unidad de medida y gracias a el borrado en cascada lo que hace es que al borrar X unidad de medida esta borra todas las categorias que dependian de ella. Es para mantener el sistema "limpio"(cascade es borrado fisico usar con cuidado, no es un borrado soft)    

class ProductCategory(BaseModel):

    description= models.CharField('Description', max_length= 50,blank= False, null= False, unique= True)
    
    
    historical = HistoricalRecords() #Tabla espejo, es el historial de cambios

    @property
    def _history_user(self):
        return self.changed_by
    
    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value
    
    
    class Meta:

        verbose_name = 'Categoria de Producto'
        verbose_name_plural = 'Categorias de Productos'
    
    def __str__(self):
        return self.description

#Clase para aplicar descuentos a categorias enteras    
class Indicador(BaseModel):

    discount_value = models.PositiveSmallIntegerField(default=0)
    category_product = models.ForeignKey(ProductCategory, on_delete= models.CASCADE, verbose_name= 'Indicador de oferta')
    
    historical = HistoricalRecords() #Tabla espejo, es el historial de cambios

    @property
    def _history_user(self):
        return self.changed_by
    
    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value
    
    
    class Meta:

        verbose_name = 'Indicador de oferta'
        verbose_name_plural = 'Indicadores de ofertas'
    
    def __str__(self):
        return f"Descuento de {self.discount_value}% para {self.category_product}"

#Clase principal de producto, asociado a una categoria

class Product(BaseModel):

    name= models.CharField('Nombre del producto', max_length= 150,blank= False, null= False, unique= True)
    description= models.TextField('Descripción de producto',blank= False, null= False, unique= False)
    product_image = models.ImageField('Imagen del producto', upload_to= 'products/', blank=True, null= True)
    product_category = models.ForeignKey(ProductCategory, on_delete= models.CASCADE, verbose_name= 'Categoria del producto')
    measure_unit = models.ForeignKey(MeasureUnit, on_delete= models.CASCADE, verbose_name= 'Unidad de Medida')
    price = models.DecimalField('Precio de venta', max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField('Stock disponible', default=0)
    historical = HistoricalRecords() #Tabla espejo, es el historial de cambios

    @property
    def _history_user(self):
        return self.changed_by
    
    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value
    
    
    class Meta:

        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def __str__(self):
        return self.name