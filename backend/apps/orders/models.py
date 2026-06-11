from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDIENTE',  'Pendiente de pago'),
        ('PAGADO',     'Pago confirmado'),
        ('VIAJE',      'En camino'),
        ('ENTREGADO',  'Entregado'),
        ('CANCELADO',  'Cancelado'),
        ('RECHAZADO',  'Rechazado'),
    ]

    DELIVERY_CHOICES = [
        ('ENVIO',  'Envío a domicilio'),
        ('RETIRO', 'Retiro en tienda'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    delivery_method = models.CharField('Método de entrega', max_length=20, choices=DELIVERY_CHOICES, default='ENVIO')
    
    shipping_name = models.CharField('Nombre', max_length=100, default='')
    shipping_last_name = models.CharField('Apellido', max_length=100, default='')
    shipping_email = models.EmailField('Email de contacto', default='')
    shipping_address = models.CharField('Dirección de entrega', max_length=255, default='', blank=True)
    
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDIENTE')
    
    transfer_confirmed = models.BooleanField('El usuario marcó que ya transfirió', default=False)
    cancel_reason = models.TextField('Motivo de cancelación', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.pk:
            anterior = Order.objects.get(pk=self.pk)
            if self.status in ['CANCELADO', 'RECHAZADO'] and anterior.status not in ['CANCELADO', 'RECHAZADO']:
                for item in self.items.all():
                    item.product.stock += item.quantity
                    item.product.save(update_fields=['stock'])
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)