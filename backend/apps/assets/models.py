from django.db import models
from apps.base.utils import optimizar_imagen

class SiteAsset(models.Model):
    name = models.CharField(max_length=100, help_text="Ej: Logo Header, Favicon, Banner Home")
    image = models.ImageField(upload_to='assets/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.image:
            # Nos aseguramos de que sea un archivo nuevo en memoria (un upload real)
            # y no el string de una URL que ya existe en la base de datos
            if hasattr(self.image, 'file'):
                imagen_comprimida = optimizar_imagen(self.image)
                if imagen_comprimida:
                    self.image = imagen_comprimida
                    
        # Ejecutamos el guardado original que impacta en la DB y en Supabase Storage
        super().save(*args, **kwargs)