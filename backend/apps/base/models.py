from django.db import models

# Create your models here.

class BaseModel(models.Model):
        #Base es como una clase "plantilla" para que tomen los otros modelos y en vez de borrarlo de la base de datos simplemente les cambia el state, los deja en false como "inoperantes" y listo. Es una clase que van a heredar todas las apps para guardar un historial de creacion, edicion o eliminacion. El borrado de cambie de state es llamado "soft" no es un borrado fisico simpemente una dada de baja. 

    id = models.AutoField(primary_key= True)
    state = models.BooleanField('Estado', default= True)
    created_date = models.DateField('Fecha de creación',auto_now= False, auto_now_add= True)
    modified_date = models.DateField('Fecha de modificación', auto_now= True, auto_now_add= False)
    deleted_date = models.DateField('Fecha de eliminación', auto_now= True, auto_now_add= False)

    class Meta:
        abstract = True
        verbose_name = 'Modelo Base'
        verbose_name_plural = 'Modelos Base'

