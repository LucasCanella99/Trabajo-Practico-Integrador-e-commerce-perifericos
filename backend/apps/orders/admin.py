from django.contrib import admin
from apps.orders.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # Bloqueamos los campos para que no se altere el historial de la factura por error
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Columnas que se van a ver en la tabla general de órdenes
    list_display = ['id', 'user', 'created_at', 'total', 'status']
    
    # Filtros rápidos en el lateral derecho
    list_filter = ['status', 'created_at']
    
    # Buscador por ID de orden o por el username del cliente
    search_fields = ['id', 'user__username']
    
    # Protegemos la cabecera para que sea de solo lectura
    readonly_fields = ['user', 'created_at', 'total']
    
    # Metemos los renglones (OrderItem) incrustados abajo de la cabecera
    inlines = [OrderItemInline]

    # Permite cambiar el estado con el desplegable directo desde la lista general
    list_editable = ['status']