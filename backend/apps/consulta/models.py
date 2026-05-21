from django.db import models

class Consulta(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)  # Se pone sola al guardar

    class Meta:
        verbose_name = "Consulta"
        verbose_name_plural = "Consultas"
        ordering = ['-creado_en']  # Las más nuevas aparecen arriba de todo

    def __str__(self):
        return f"Consulta de {self.nombre} ({self.email})"