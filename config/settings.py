from pathlib import Path
import os
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
CF_TOKEN = env("CF_TOKEN")
CF_ID = env("CF_ID")

DEBUG = os.environ.get("DEPLOY") != "DEPLOY"
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
STATIC_ROOT = "/srv/docker-data/static/"

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3080",
    "http://127.0.0.1:3000",
]

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

# 배포 쿠키
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://115.85.181.9:6379",
#         "TIMEOUT": 60 * 60,
#         "OPTIONS": {
#             "PASSWORD": env("REDIS_PASSWORD"),  # Update the password
#             "DB": 1,
#         },
#     }
# }

# SESSION_CACHE_ALIAS = "default"

# SESSION_ENGINE = "redis_sessions.session"
# SESSION_REDIS = {
#     "host": "115.85.181.9",
#     "port": 6379,
#     "db": 0,
#     "password": env("REDIS_PASSWORD"),  # Update the password
#     "prefix": "session",
#     "socket_timeout": 1,
#     "retry_on_timeout": True,
# }
