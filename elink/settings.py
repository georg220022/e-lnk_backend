import os
import redis
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
from django.core.cache import cache

load_dotenv()


TG_CHAT_DATA = [
                os.getenv('TELEGRAM_CHAT_1'),
                os.getenv('TELEGRAM_CHAT_2'),
                os.getenv('TELEGRAM_CHAT_3'),
                ]

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

ACCESS_TIME = os.getenv('ACCESS_TIME')
REFRESH_TIME = os.getenv('REFRESH_TIME')
TIME_SAVE_COOKIE = os.getenv('TIME_SAVE_COOKIE')

CACHE_TABLE = os.getenv('CACHE_TABLE')

APPEND_SLASH = True
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS')
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True #os.getenv('DEBUG')
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'users.User'
SITE_NAME = os.getenv('SITE_NAME')

EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

REDIS_DB_ACTIVATE = os.getenv('REDIS_DB_ACTIVATE')
REDIS_DB_STAT = os.getenv('REDIS_DB_STAT')
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_DB = os.getenv('REDIS_DB')
REDIS_PASS = os.getenv('REDIS_PASS')
REDIS_LOCATION = os.getenv('REDIS_LOCATION')
REDIS_DB_CACHE = os.getenv('REDIS_DB_CACHE')
DB_USER = os.getenv('DB_USER')
REDIS_FOR_ACTIVATE = redis.StrictRedis(
                               host=REDIS_HOST,
                               port=REDIS_PORT,
                               db=REDIS_DB_ACTIVATE,
                               password=REDIS_PASS,
                               )
REDIS_BASE_FOR_LINK = redis.StrictRedis(
                               host=REDIS_HOST,
                               port=REDIS_PORT,
                               db=REDIS_DB,
                               password=REDIS_PASS,
                               )
REDIS_BASE_FOR_STAT = redis.StrictRedis(
                                        host=REDIS_HOST,
                                        port=REDIS_PORT,
                                        db=REDIS_DB_STAT,
                                        password=REDIS_PASS,
                                       )


CELERY_BROKER_URL = f'redis://:{REDIS_PASS}@redis_db:{REDIS_PORT}/{REDIS_DB_STAT}' # Пока запускаю в докере - redis_db
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
"""CELERY_BEAT_SCHEDULE = {
    'updater_week_stat': {
        'task': 'persoal_area.tasks.updater_week_stat',
        'schedule': crontab(minute="*/1"),
    },
}"""


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

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '/media/')

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


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE'),
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT')
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
        'user': os.getenv('USER'),
        'anon': os.getenv('ANON'),
        'create_link_user': os.getenv('CREATE_LINK_USER'),
        'create_link_anonym': os.getenv('CREATE_LINK_ANONYM'),
        'user_pass_try': os.getenv('USER_PASS_TRY'),
        'anon_pass_try': os.getenv('ANON_PASS_TRY'),
        'anon_registration': os.getenv('ANON_REGISTRATION'),
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
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(ACCESS_TIME)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(REFRESH_TIME)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    'USER_ID_FIELD': 'public_key',
    'JTI_CLAIM': 'jti',
}

data = {
        'no_reload_day': 0,
        'new_users': 0,
        'send_msg_email': 0,
        'activated': 0,
        'guest_link': 0,
        'reg_link': 0,
        'redirect': 0,
        'refresh_tokens': 0,
        'good_enter': 0,
        'bad_enter': 0,
        'bad_try_activated': 0,
        'reporteds': {}
    }
cache.set_many(data)
