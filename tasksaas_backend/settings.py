
from pathlib import Path
from decouple import config
import cloudinary
import cloudinary.uploader
import cloudinary.api



# Cloudflare R2 Configuration
CLOUDFLARE_R2_BUCKET = config("CLOUDFLARE_R2_BUCKET")
CLOUDFLARE_R2_BUCKET_ENDPOINT = config("CLOUDFLARE_R2_BUCKET_ENDPOINT")
CLOUDFLARE_R2_ACCESS_KEY = config("CLOUDFLARE_R2_ACCESS_KEY")
CLOUDFLARE_R2_SECRET_KEY = config("CLOUDFLARE_R2_SECRET_KEY")
CLOUDFLARE_R2_PUBLIC_URL = config("CLOUDFLARE_R2_PUBLIC_URL")

# AWS S3 / Cloudflare R2 Settings
AWS_ACCESS_KEY_ID = CLOUDFLARE_R2_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = CLOUDFLARE_R2_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = CLOUDFLARE_R2_BUCKET
AWS_S3_ENDPOINT_URL = CLOUDFLARE_R2_BUCKET_ENDPOINT
AWS_S3_REGION_NAME = 'auto'  # Cloudflare R2 uses 'auto'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = True
AWS_S3_CUSTOM_DOMAIN = CLOUDFLARE_R2_PUBLIC_URL.replace('https://', '').replace('http://', '')

# Use Cloudflare R2 for default file storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-%czi_^6texrx)h7@d#x58rp7s#(jl*#idtou14ol%-_%z=)bm4')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# Parse ALLOWED_HOSTS from environment variable
ALLOWED_HOSTS = [host.strip() for host in config('ALLOWED_HOSTS', default='taskprime.app,127.0.0.1,192.168.1.70').split(',')]


CORS_ALLOW_HEADERS = ['*']
CORS_ALLOW_METHODS = ['*']
CORS_ALLOW_CREDENTIALS = True

# For development only - remove in production
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'storages',  # For Cloudflare R2 storage
    'app1',
    'PunchIn',
    'corsheaders',
    'cloudinary',
    'DebtorsAPI',
    'suppiers_api',
    'accesscontroll',
    'users_api',
    'area',
    'Collection',
    'item_orders',
]

# Parse CORS origins from environment variable
CORS_ALLOWED_ORIGINS = [
    origin.strip() 
    for origin in config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173,https://taskprime.app,https://192.168.1.70:5173').split(',')
]

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=1, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
}
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Allow all by default
    ],
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'tasksaas_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tasksaas_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='eway'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='admin'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'TIME_ZONE': config('DB_TIMEZONE', default='Asia/Kolkata'),
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 seconds query timeout
        },
        'CONN_MAX_AGE': 600,  # Connection pooling - 10 minutes
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/


LANGUAGE_CODE = 'en-us'
TIME_ZONE = config('DB_TIMEZONE', default='Asia/Kolkata')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

import os

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


