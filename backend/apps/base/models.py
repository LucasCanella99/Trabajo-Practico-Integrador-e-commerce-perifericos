from django.db import models

# Create your models here.

class BaseModel(models.Model):
    state        = models.BooleanField(default=True)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    deleted_date  = models.DateField(null=True, blank=True)  # ← Sin auto_now

    def delete_logical(self):
        """Método explícito para hacer el soft delete correctamente"""
        from django.utils import timezone
        self.state = False
        self.deleted_date = timezone.now().date()  # ← Se guarda solo cuando se llama
        self.save()

# Se realizaron cambios debido a que deleted_date tenía exactamente el mismo comportamiento que modified_date. Nunca guardaba la fecha real en que el registro fue dado de baja.
