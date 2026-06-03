from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.base.utils import optimizar_imagen

User = get_user_model()

class Order(models.Model):
    # Estados personalizados para simular el ciclo de vida real de la venta
    STATUS_CHOICES = [
        ('REVISION', 'Pendiente de aprobación / En revisión'),
        ('PAGADO', 'Pago confirmado / Pendiente de envío'),
        ('VIAJE', 'En viaje / Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # max_digits=10 y decimal_places=2 te permite guardar montos de hasta $99.999.999,99
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    comprobante_pago = models.ImageField('Comprobante de Pago', upload_to='comprobantes/', blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='REVISION'  # Por defecto el usuario ve en revision el estado de la compra
    )

    class Meta:
        ordering = ['-created_at']  # Las órdenes más nuevas aparecen primero

    def __str__(self):
        return f"Orden {self.id} - {self.user.username} ({self.get_status_display()})"

    # Inyectamos el método save para optimizar el comprobante antes de mandarlo a Supabase
    def save(self, *args, **kwargs):
        # 1. Lógica para el comprobante 
        if self.comprobante_pago:
            if hasattr(self.comprobante_pago, 'file'):
                imagen_comprimida = optimizar_imagen(self.comprobante_pago)
                if imagen_comprimida:
                    self.comprobante_pago = imagen_comprimida
        
        # 2. Lógica para reponer stock al CANCELAR
        if self.pk:  # Si la orden ya existe en la DB
            orden_anterior = Order.objects.get(pk=self.pk)
            # Si el estado cambió a CANCELADO y antes NO lo estaba
            if self.status == 'CANCELADO' and orden_anterior.status != 'CANCELADO':
                for item in self.items.all():
                    item.product.stock += item.quantity
                    item.product.save()
                    
        # 3. Guardado final
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items') # Evita que si se elimina el producto mas adelante, no se borre la orden que tenia ese producto
    quantity = models.PositiveIntegerField(default=1)
    
    # Acá se congela el precio del producto en el segundo exacto de la compra
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Orden {self.order.id})"