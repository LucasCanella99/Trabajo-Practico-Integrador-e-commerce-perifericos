import os
from pathlib import Path
from .base import *

# Resolvemos la ruta base para cargar correctamente las variables de entorno
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Configuración de Base de Datos Dinámica
if os.getenv('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'backend' / 'db.sqlite3',
        }
    }

# -------------------------------------------------------------------
# Configuración de Almacenamiento Dinámico (Supabase Bucket / Local)
# -------------------------------------------------------------------
if os.getenv('AWS_STORAGE_BUCKET_NAME'):
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": os.getenv('AWS_ACCESS_KEY_ID'),
                "secret_key": os.getenv('AWS_SECRET_ACCESS_KEY'),
                "bucket_name": os.getenv('AWS_STORAGE_BUCKET_NAME'),
                "endpoint_url": os.getenv('AWS_S3_ENDPOINT_URL'),
                "region_name": os.getenv('AWS_S3_REGION_NAME', 'sa-east-1'),
                "querystring_auth": False,
                "file_overwrite": False,
            },
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }