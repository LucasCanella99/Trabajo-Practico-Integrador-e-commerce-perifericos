from django.contrib import admin
from .models import Consulta

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    # Lo que ve el vendedor en la tabla general
    list_display = ['nombre', 'email', 'creado_en']
    # Filtro rápido por fecha
    list_filter = ['creado_en']
    # Buscador por nombre o por correo
    search_fields = ['nombre', 'email']
    
    # Hacemos que todo sea de solo lectura para que el vendedor no edite el mensaje sin querer
    readonly_fields = ['nombre', 'email', 'mensaje', 'creado_en']
