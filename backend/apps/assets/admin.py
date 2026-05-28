from django.contrib import admin
from .models import SiteAsset

@admin.register(SiteAsset)
class SiteAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at') # Esto es para que se vean columnas en el admin
    search_fields = ('name',)