from django.db import models
from django.conf import settings #Para evitar las importaciones circular no se importa directamente de la app user
from apps.base.models import BaseModel #Heredamos de base para el borrado logico y el historial
from apps.products.models import Product

# Create your models here.

class Cart(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name= 'cart') # Apunta a un usuario

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural= 'Carritos'
    
    def __str__(self):
        return f"Carrito de {self.user.username} (Estado: {self.state})"
    
class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete= models.CASCADE, related_name='items') # Muchos items puede pertenecer al  mismo carrito

    product = models.ForeignKey(Product, on_delete= models.CASCADE) #Varios carritos pueden tener el mismo producto

    quantity = models.PositiveIntegerField(default = 1) #Cantidad, por defecto uno al agregar al carrito

    class Meta:
        verbose_name = 'Item de carrito'
        verbose_name_plural= 'Items de carrito'
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (En el {self.cart})"