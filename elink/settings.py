import os
import redis
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta


load_dotenv()

APPEND_SLASH = False
ALLOWED_HOSTS = 
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG')
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'users.User'
SITE_NAME = os.getenv('SITE_NAME')

REDIS_DB_STAT = os.getenv('REDIS_DB_STAT')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')
REDIS_PASS = os.getenv('REDIS_PASS')
REDIS_LOCATION = os.getenv('REDIS_LOCATION')
REDIS_DB_CACHE = os.getenv('REDIS_DB_CACHE')
REDIS_BASE_FOR_LINK = redis.StrictRedis(host=REDIS_HOST,
                               port=REDIS_PORT,
                               db=REDIS_DB,
                               password=REDIS_PASS)
REDIS_BASE_FOR_STAT = redis.StrictRedis(host=REDIS_HOST,
                               port=REDIS_PORT,
                               db=REDIS_DB_STAT,
                               password=REDIS_PASS)


INSTALLED_APPS = [
    'rest_framework_simplejwt.token_blacklist',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'djoser',
    'elink_redirect',
    'users',
    'elink_index',
    'personal_area',
    #'rest_framework_simplejwt.token_blacklist',
    
    #'rest_framework.authtoken',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'elink.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join('templates')],
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

WSGI_APPLICATION = 'elink.wsgi.application'

"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',#os.getenv('DB_ENGINE'),
        'NAME': 'postgres',#os.getenv('DB_NAME'),
        'USER': 'elink_user',#os.getenv('DB_USER'),
        'PASSWORD': 'iBgnBj4bcWzXLEMWQ7BwQ593xu1UWMubm0russia',#os.getenv('DB_PASSWORD'),
        'HOST': '127.0.0.1',#os.getenv('DB_HOST'),
        'PORT': '5432'#os.getenv('DB_PORT')
    }
}

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

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    #'DEFAULT_AUTHENTICATION_CLASSES': [
    #    'rest_framework.authentication.BasicAuthentication',
    #    'rest_framework.authentication.SessionAuthentication',
    #],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', 
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        # Глобальные рейты на все остальное
        'user': '250/hour',
        'anon': '80/hour',
        # Локальные рейты создание ссылок
        'create_link_user': '1000/hour',
        'create_link_anonym': '1000/hour',
        # Рейты ввода пароля
        'user_pass_try': '50/hour',
        'anon_pass_try': '25/hour',
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_DB_CACHE,
        'OPTIONS': {
            'PASSWORD': REDIS_PASS,
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'JTI_CLAIM': 'jti',
}
