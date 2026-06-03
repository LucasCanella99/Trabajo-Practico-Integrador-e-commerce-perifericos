import os
import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['e-commerce-perifericos-backend.onrender.com']

# 1. BASE DE DATOS (PostgreSQL de Supabase)
DATABASES = {
    'default': dj_database_url.config(
        default=f"postgres://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASSWORD')}@{os.environ.get('DB_HOST')}:{os.environ.get('DB_PORT')}/{os.environ.get('DB_NAME')}",
        conn_max_age=600
    )
}

# 2. ALMACENAMIENTO (Bucket de Supabase / S3)
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Credenciales del Bucket mapeadas con las variables de entorno de Render
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL') # La URL de Supabase S3
AWS_DEFAULT_ACL = None 
AWS_QUERYSTRING_AUTH = False

# Configuraciones extra opcionales para el comportamiento de los archivos
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_DEFAULT_ACL = None  # Supabase maneja los accesos con sus propias políticas de la App

STATIC_URL = 'static/'

#para los recuperar contraseña y verificar mails

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.resend.com'
EMAIL_HOST_USER = 'resend' 
EMAIL_HOST_PASSWORD = os.environ.get('RESEND_API_KEY') 
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'onboarding@resend.dev'

# Esta es la URL que la librería usa para construir el link que llega al mail.
# Cambiar por URL real de producción cuando lo tengamos .
# PASSWORD_RESET_FRONTEND_URL = "https://dominio-real.com/reset-confirm/"