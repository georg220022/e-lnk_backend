import os
import redis
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
from django.core.cache import cache

load_dotenv()

TG_CHAT_DATA = [
    os.getenv("TELEGRAM_CHAT_1"),
    os.getenv("TELEGRAM_CHAT_2"),
    os.getenv("TELEGRAM_CHAT_3"),
]

CSRF_TRUSTED_ORIGINS = ["https://e-lnk.ru", ]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

ACCESS_TIME = os.getenv("ACCESS_TIME")
REFRESH_TIME = os.getenv("REFRESH_TIME")
TIME_SAVE_COOKIE = os.getenv("TIME_SAVE_COOKIE")

APPEND_SLASH = False
ALLOWED_HOSTS = [
    "*",
    "127.0.0.1:8000",
    "46.229.214.129",
    "127.0.0.1",
    "e-lnk.ru",
    "https://e-lnk.ru",
]
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = "users.User"

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_TLS = False
EMAIL_USE_SSL = True

REDIS_DB_COUNT = os.getenv("REDIS_DB_COUNT")
REDIS_DB_LNK_CACHE = os.getenv("REDIS_DB_LNK_CACHE")
REDIS_DB_ACTIVATE = os.getenv("REDIS_DB_ACTIVATE")
REDIS_DB_STAT = os.getenv("REDIS_DB_STAT")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_DB = os.getenv("REDIS_DB")
REDIS_PASS = os.getenv("REDIS_PASS")
REDIS_LOCATION = os.getenv("REDIS_LOCATION")
REDIS_DB_CACHE = os.getenv("REDIS_DB_CACHE")
DB_USER = os.getenv("DB_USER")
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
    decode_responses=True,  # Эксперимент (read_write_base decode)
)
REDIS_BASE_FOR_STAT = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB_STAT,
    password=REDIS_PASS,
)
REDIS_BASE_FOR_COUNT = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB_COUNT,
    password=REDIS_PASS,
    # decode_responses=True
)
REDIS_BASE_FOR_CACHE_LINK = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB_LNK_CACHE,
    password=REDIS_PASS,
    # decode_responses=True
)

CELERY_BROKER_URL = f"redis://:{REDIS_PASS}@127.0.0.1:{REDIS_PORT}/{REDIS_DB_STAT}"  # Пока запускаю в докере - redis_db
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "elink_redirect",
    "users",
    "elink_index",
    "personal_area",
    "service",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if DEBUG:
    MIDDLEWARE += [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
        "debug_toolbar_force.middleware.ForceDebugToolbarMiddleware",
    ]
    INSTALLED_APPS += ["debug_toolbar",]

ROOT_URLCONF = "elink.urls"

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "/media/")

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join("templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "elink.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE"),
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "99999/hour", #os.getenv("USER"),
        "anon": "99999/hour", #os.getenv("ANON"),
        "create_link_user": "99999/hour", #os.getenv("CREATE_LINK_USER"),
        "create_link_anonym": "99999/hour", #os.getenv("CREATE_LINK_ANONYM"),
        "user_pass_try": "99999/hour", #os.getenv("USER_PASS_TRY"),
        "anon_pass_try": "99999/hour", #os.getenv("ANON_PASS_TRY"),
        "anon_registration": "99999/hour", #os.getenv("ANON_REGISTRATION"),
        "pass_open_anon": "99999/hour", #os.getenv("ANON_TRY_PASS"),
        "pass_open_user": "99999/hour", #os.getenv("USER_TRY_PASS"),
    },
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_DB_CACHE,
        "OPTIONS": {
            "PASSWORD": REDIS_PASS,
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(ACCESS_TIME)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(REFRESH_TIME)),
    "ROTATE_REFRESH_TOKENS": False, # Было тру
    "BLACKLIST_AFTER_ROTATION": False, # Было тру
    "UPDATLAST_LOGIN": False,
    "USER_ID_FIELD": "public_key",
    #"JTI_CLAIM": "jti", было включено
}

JAZZMIN_UI_TWEAKS = {
    "theme": "cosmo",
}

JAZZMIN_SETTINGS = {
    "site_title": "Панель управления",
    "site_header": "E-LNK",
    "site_brand": "E-LNK",
    "site_logo": "admin/img/logos.png",
    "login_logo": True,
    "login_logo_dark": None,
    "site_logo_classes": "img-thumbnail",
    "site_icon": "admin/img/logos.png",
    "welcome_sign": "E-LNK Dashboard",
    "copyright": "E-lnk.ru",
    "search_model": "users.User",
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Написать разработчику", "url": "https://t.me/georg2022bcknd", "new_window": True},
        {"name": "Открыть сайт", "url": "https://e-lnk.ru", "new_window": True},

    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {"auth.user": "collapsible", "auth.group": "vertical_tabs"},
    "language_chooser": False,
}

ADMINS = [ ('Georg', 'help@e-lnk.ru') ]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_format": {
            "format": "[{module} {asctime} {levelname}] - {message} - {filename} - {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            "filename": "logs/debug.log",
            "formatter": "default_format",
        },
        "mail_admins": {
            "level": 'ERROR',
            "class": 'django.utils.log.AdminEmailHandler',
            "include_html": True,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "WARNING",
            "propagate": True,
        },
    },
}
# cache.clear()
# Техническая информация для отправки в telegram администратора(ов) ( Prometheus для бедных xD )
stat_data = {
    "server_no_long_link": 0, # Не верная длина ссылки
    "server_check_pass": 0, # Обращение к ссылке с паролем
    "server_open_bad_time": 0, # Открытий ссылки с истекшим сроком
    "server_bad_data": 0, # Сколько раз не получен "shortCode" и-или "linkPassword"
    "server_bad_edit_descrip": 0, # Сколько раз не верно изменили описание
    "server_bad_try_create_user_link": 0, # Попыток создания ссылки без активированной учетной записи
    "server_bad_valid_serializer_create_link": 0, # Не прошло валидацию создание ссылки от юзера
    "server_bad_delete_link": 0, # Плохих попыток удаления ссылки
    "server_bad_update_desrip_link": 0, # Плохих попыток изменить описание
    "server_redis_redirect": 0, # Переходов по Redis ссылке (гостевой)
    "server_open_bad_link": 0, # Попыток открыть не существующие ссылки
    "server_bad_input_pass": 0, # Не верных вводов пароля
    "server_good_input_pass": 0, # Верных вводов пароля
    "server_empty_pass_open_lnk": 0, # Пришло пустых паролей
    "server_get_stat_in_cache": 0, # Сколько раз взяли статистику панели из кеша
    "server_get_stat_in_serializer": 0, # Сколько раз взяли статистику НЕ из кеша
    "server_unknown_coutry": 0, # Не удалось определить страну
    "server_redis_atribute_error": 0, # Взять из базы редиса не существующую ссылку
    "server_redis_index_error": 0, # Взять из базы редиса не существующую ссылку
    "server_pstgrs_obj_doesnt_exist": 0, # Взять из базы постгреса не существующую ссылку
    "server_bad_send_pdf_day_stat": 0, # Не удачных отправок ежедневной статы
    "server_need_clear_cache": 0, # Досрочных запросов на запись кликов из кеша в БД
    "server_user_reg_limit_lnk": 0, # Сколько разполучено сообщение о лимите ссылок обычному юзеру
    "server_user_btest_limit_lnk": 0, # Сколько разполучено сообщение о лимите ссылок бетатестерам
    "server_try_create_lnk_ban_usr": 0, # Попыток оздаь ссылку забаннным юзеом
    "serveстерr_bad_try_update_refresh": 0, # Неудачных попыток обновить refresh token
    "server_bad_change_pass": 0, # Неудачных попыток сменить пароль
    "server_good_change_pass": 0, # Удачно смененные пароли
    "server_error_register": 0, # Ошибок при регистрации
    "server_logout_account": 0, # Логаутов из аккаунта
    "server_enter_notfound_email": 0, # Попыток входа с несуществующим емейлом
    "server_guest_link": 0, # Количество ссылок от гостей
    "server_delete_link": 0, # Ссылок удалено пользователями
    "server_update_desrip_link": 0, # Обновлено описаний
    "server_new_users": 0, # Новых пользователей
    "server_send_msg_email": 0, # Отправлено активаций
    "server_activated": 0, # Активированно аккаунтов
    "server_reg_link": 0, # Количество ссылок от зарегестрированных юзеров
    "server_redirect": 0, # Переходов за сегодня
    "server_refresh_tokens":  0, # Обновлено токенов
    "server_good_enter": 0, # Входов в аккаунт удачных (ввести логин-пароль)
    "server_bad_enter": 0, # Входов в аккаунт НЕ удачных (ввести логин-пароль)
    "server_bad_try_activated": 0, # Неудачных попыток активации
}
cache.set_many(stat_data, None)

#  Параметры не для обслуживания сервера, не обнуляются в фоновых задачах по окончании дня
technical_data = {
    "send_critical_msg": "No",
    "live_cache": 10,
    "count_cache_infolink": 0,
    "no_reload_day": 0,
    "reporteds": {},
    "time_service": {}
}
cache.set_many(technical_data, None)
