from django.contrib import admin
from apps.carts.models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'state')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'state')


admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)