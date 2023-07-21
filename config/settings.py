from pathlib import Path
import os
import environ
import pymysql

pymysql.install_as_MySQLdb()

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
CF_TOKEN = env("CF_TOKEN")
CF_ID = env("CF_ID")

DEBUG = False
ALLOWED_HOSTS = ["*"]

THIRD_PARTY_APPS = [
    "corsheaders",
    "drf_yasg",
    "rest_framework",
    "rest_framework_simplejwt",
    "debug_toolbar",
]

CUSTOM_APPS = [
    "accessinfo.apps.AccessinfoConfig",
    "users.apps.UsersConfig",
    "feeds.apps.FeedsConfig",
    "groups.apps.GroupsConfig",
    "categories.apps.CategoriesConfig",
    "comments.apps.CommentsConfig",
    "likes.apps.LikesConfig",
    "medias.apps.MediasConfig",
    "letterlist.apps.LetterlistConfig",
    "auth_sms.apps.AuthSmsConfig",
]

SYSTEM_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

INSTALLED_APPS = SYSTEM_APPS + CUSTOM_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
INTERNAL_IPS = ["127.0.0.1"]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "config.wsgi.application"

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

LANGUAGE_CODE = "ko-KR"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(BASE_DIR, "static")

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://115.85.181.9",
    "http://115.85.181.9",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "https://curb.site",
    "https://www.curb.site",
    "https://backend.curb.site",
    "https://dev.curb.site",
]

if os.environ.get("DEPLOY") == "DEPLOY":
    SESSION_COOKIE_DOMAIN = ".curb.site"
    CSRF_COOKIE_DOMAIN = ".curb.site"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.User"


import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if os.environ.get("SERVER") == "NAVER":
    sentry_sdk.init(
        dsn="https://c0fee42386b94b578ecdc3a6a032555e@o4504859857387520.ingest.sentry.io/4504996177903616",
        integrations=[
            DjangoIntegration(),
        ],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_NAME"),
            "USER": env("POSTGRES_USER"),
            "PASSWORD": env("POSTGRES_PASSWORD"),
            "HOST": env("POSTGRES_HOST"),
            "PORT": env("POSTGRES_PORT"),
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

if os.environ.get("SERVER") == "NAVER":
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://redis:6379",
            "TIMEOUT": 60 * 60,
            "OPTIONS": {
                "PASSWORD": env("REDIS_PASSWORD"),  # Update the password
                "DB": 2,
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://115.85.181.9:6379",
            "TIMEOUT": 60 * 60,
            "OPTIONS": {
                "PASSWORD": env("REDIS_PASSWORD"),  # Update the password
                "DB": 1,
            },
        }
    }


def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable".format(var_name)
        # raise ImproperlyConfigured(error_msg)


SECRET_KEY = get_env_variable("DJANGO_SECRET")

# 데이터베이스는 AWS RDS Mysql 사용 했습니다.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": get_env_variable("DATABASE"),
        "USER": get_env_variable("DB_USER"),
        "PASSWORD": get_env_variable("DB_PASSWORD"),
        "HOST": get_env_variable("DB_HOST"),
        "PORT": get_env_variable("DB_PORT"),
        "OPTIONS": {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

SESSION_CACHE_ALIAS = "default"

SESSION_ENGINE = "redis_sessions.session"
SESSION_REDIS = {
    "host": "115.85.181.9",
    "port": 6379,
    "db": 0,
    "password": env("REDIS_PASSWORD"),  # Update the password
    "prefix": "session",
    "socket_timeout": 1,
    "retry_on_timeout": True,
}
