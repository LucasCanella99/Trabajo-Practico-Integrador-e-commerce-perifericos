from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Carga limpia del archivo .env
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("¡ERROR CRÍTICO: La variable SECRET_KEY no está configurada en el entorno!")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS =[
    'apps.users',
    'apps.base',
    'apps.products',
    'apps.carts',
    'apps.orders',
    'apps.consulta',
    'apps.assets',
]

THIRD_APPS = [
    'rest_framework',
    'simple_history',
    'django_rest_passwordreset',
    'axes',
]


INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'axes.middleware.AxesMiddleware',  
]

ROOT_URLCONF = 'ecommerce_rest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce_rest.wsgi.application'

# específica e independiente dentro de local.py y production.py

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = 'users.User'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


STORAGES = {
       "default": {
           "BACKEND": "django.core.files.storage.FileSystemStorage",
       },
       "staticfiles": {
           "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
       },
   }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework Configuration
REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Le decimos a DRF que busque el token JWT en el header Authorization
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    #ESCUDO CONTRA SPAM (Throttling) Por lo del contacto que va a ser publico
    'DEFAULT_THROTTLE_CLASSES': [
        # Rastrea la IP del usuario que no inició sesión
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        # Máximo 1 consulta por minuto por cada IP anónima
        'anon': '1/minute',
    }
}

SIMPLE_JWT = {
    # El access token dura poco por seguridad
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    # El refresh token dura más, el usuario no tiene que loguearse tan seguido
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    # Cuando usás el refresh para renovar, te manda también un refresh nuevo
    'ROTATE_REFRESH_TOKENS': True,
}

# La URL con la que el navegador va a pedir las fotos de forma local
MEDIA_URL = '/media/'

# La carpeta física real  donde se van a crear 'products/' y 'comprobantes/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',  # ← primero Axes intercepta
    'django.contrib.auth.backends.ModelBackend',
]


AXES_FAILURE_LIMIT = 3                                    # intentos antes de bloquear
AXES_COOLOFF_TIME = timedelta(minutes=15)                 # tiempo de bloqueo
AXES_LOCKOUT_PARAMETERS = [['username', 'ip_address']]    # bloquea la combinación usuario+IP
AXES_RESET_ON_SUCCESS = True                              # si entra bien, resetea el contador
AXES_LOCKOUT_CALLABLE = 'apps.users.utils.lockout_response'