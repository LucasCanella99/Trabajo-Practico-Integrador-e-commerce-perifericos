import os
import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['e-commerce-perifericos-backend.onrender.com']

# Configuración de Base de Datos para Producción (Supabase)
DATABASES = {
    'default': dj_database_url.config(
        # Levanta automáticamente las credenciales desde la URL que maneja Render interna o tu string
        default=f"postgres://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}",
        conn_max_age=600
    )
}

# Dejamos que WhiteNoise maneje los estáticos en producción
STATIC_URL = 'static/'