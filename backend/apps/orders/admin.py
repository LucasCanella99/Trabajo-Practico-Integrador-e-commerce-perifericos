from django.contrib import admin
from django.utils.html import format_html
from apps.orders.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'total', 'status', 'ver_comprobante']
    readonly_fields = ['user', 'created_at', 'total', 'ver_comprobante'] # Agregamos ver_comprobante acá
    inlines = [OrderItemInline]
    list_editable = ['status']

    # Esta función crea la vista previa segura
    def ver_comprobante(self, obj):
        if obj.comprobante_pago:
            return format_html('<a href="{}" target="_blank"><img src="{}" style="width:100px;" /></a>', 
                               obj.comprobante_pago.url, obj.comprobante_pago.url)
        return "Sin comprobante"
    ver_comprobante.short_description = "Comprobante"