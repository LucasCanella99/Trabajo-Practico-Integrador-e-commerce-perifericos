from django.db import models

# Create your models here.

class BaseModel(models.Model):
    id           = models.AutoField(primary_key= True)
    state        = models.BooleanField('Estado', default=True)
    created_date = models.DateField('Fecha de creación', auto_now=False, auto_now_add=True)
    modified_date = models.DateField('Fecha de modificación', auto_now=True, auto_now_add=False)
    deleted_date  = models.DateField('Fecha de eliminación', null=True, blank=True)  # ← Sin auto_now

    class Meta:
        abstract = True
        verbose_name = 'Modelo Base'
        verbose_name_plural = 'Modelos Base'

    def delete_logical(self):
        """Método explícito para hacer el soft delete correctamente"""
        from django.utils import timezone
        self.state = False
        self.deleted_date = timezone.now().date()  # ← Se guarda solo cuando se llama
        self.save()

# Se realizaron cambios debido a que deleted_date tenía exactamente el mismo comportamiento que modified_date. Nunca guardaba la fecha real en que el registro fue dado de baja.
