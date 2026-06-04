# apps/orders/admin.py
from django.contrib import admin
from apps.orders.models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    readonly_fields = ['product', 'quantity', 'price']
    can_delete      = False
    extra           = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'shipping_name', 'shipping_last_name', 'total', 'status', 'transfer_confirmed', 'created_at']
    list_filter   = ['status', 'transfer_confirmed']
    search_fields = ['user__username', 'user__email', 'shipping_email', 'shipping_name']
    list_editable = ['status']
    readonly_fields = ['user', 'created_at', 'updated_at', 'total', 'shipping_name', 'shipping_last_name', 'shipping_email', 'shipping_address', 'cancel_reason']
    inlines = [OrderItemInline]

    fieldsets = [
        ('Datos del pedido', {'fields': ['user', 'created_at', 'updated_at', 'total', 'status']}),
        ('Datos de envío', {'fields': ['shipping_name', 'shipping_last_name', 'shipping_email', 'shipping_address']}),
        ('Pago y cancelación', {'fields': ['transfer_confirmed', 'cancel_reason']}),
    ]

    actions = ['aprobar_pagos', 'rechazar_pedidos', 'marcar_en_camino', 'marcar_entregado']

    def aprobar_pagos(self, request, queryset):
        actualizadas = 0
        for order in queryset.filter(status='PENDIENTE', transfer_confirmed=True):
            order.status = 'PAGADO'
            order.save(update_fields=['status', 'updated_at'])
            actualizadas += 1
        self.message_user(request, f'{actualizadas} orden(es) confirmadas como pagadas ✓')
    aprobar_pagos.short_description = '✓ Confirmar pago (transfirió)'

    def rechazar_pedidos(self, request, queryset):
        count = 0
        for order in queryset.exclude(status__in=['CANCELADO', 'RECHAZADO', 'ENTREGADO']):
            order.status = 'RECHAZADO'
            order.save()
            count += 1
        self.message_user(request, f'{count} orden(es) rechazadas y stock repuesto ✓')
    rechazar_pedidos.short_description = '✕ Rechazar (repone stock)'

    def marcar_en_camino(self, request, queryset):
        actualizadas = queryset.filter(status='PAGADO').update(status='VIAJE')
        self.message_user(request, f'{actualizadas} orden(es) marcadas como En camino 🚚')
    marcar_en_camino.short_description = '🚚 Marcar como En camino'

    def marcar_entregado(self, request, queryset):
        actualizadas = queryset.filter(status='VIAJE').update(status='ENTREGADO')
        self.message_user(request, f'{actualizadas} orden(es) marcadas como Entregadas ✓')
    marcar_entregado.short_description = '📦 Marcar como Entregado'