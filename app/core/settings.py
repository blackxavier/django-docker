import os
import dj_database_url  # Import dj_database_url
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def get_env_variable(var_name, default=None):
    value = os.environ.get(var_name, default)
    # Allow None to be returned if default is explicitly None and var_name is not found
    if value is None and default is not None:
        raise ImproperlyConfigured(
            f"The {var_name} environment variable is not set and no default value was provided."
        )
    return value


# Use the updated function to set SECRET_KEY with a fallback value
SECRET_KEY = get_env_variable(
    "SECRET_KEY", "fallback-secret-key-for-heroku-build"
)  # Fallback for build time

DEBUG = bool(int(os.environ.get("DEBUG", default=0)))

# Configure ALLOWED_HOSTS for Heroku
HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
if HEROKU_APP_NAME:
    ALLOWED_HOSTS.append(f"{HEROKU_APP_NAME}.herokuapp.com")
# Add your custom domain if you have one
# ALLOWED_HOSTS.append('yourcustomdomain.com')


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",  # Add whitenoise
    "django.contrib.staticfiles",
    "upload",
    "counter",
    "storages",  # For django-storages (S3)
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Add whitenoise middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

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

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=True)}
else:
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get("APP_SQL_ENGINE", "django.db.backends.sqlite3"),
            "NAME": os.environ.get("APP_SQL_DATABASE", BASE_DIR / "db.sqlite3"),
            "USER": os.environ.get("APP_SQL_USER", "user"),
            "PASSWORD": os.environ.get("APP_SQL_PASSWORD", "password"),
            "HOST": os.environ.get("APP_SQL_HOST", "localhost"),
            "PORT": os.environ.get("APP_SQL_PORT", "5432"),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "MinimumLengthValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "CommonPasswordValidator"),
    },
    {
        "NAME": ("django.contrib.auth.password_validation." "NumericPasswordValidator"),
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# CSRF settings for Heroku
CSRF_TRUSTED_ORIGINS = []
if HEROKU_APP_NAME:
    CSRF_TRUSTED_ORIGINS.append(f"https://{HEROKU_APP_NAME}.herokuapp.com")
# Add your custom domain if you have one
# CSRF_TRUSTED_ORIGINS.append('https://yourcustomdomain.com')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
# Add whitenoise storage for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Media files (User uploads) - Configure for S3
MEDIA_URL = "/media/"
if "AWS_STORAGE_BUCKET_NAME" in os.environ:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.environ.get(
        "AWS_S3_REGION_NAME", "us-east-1"
    )  # Example region
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None  # Or 'public-read' if you want files to be public by default
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
    MEDIA_ROOT = MEDIA_URL  # Not used by S3 storage but good to set
else:
    MEDIA_ROOT = BASE_DIR / "mediafiles"
    os.makedirs(MEDIA_ROOT, exist_ok=True)

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Caches - Configure for Heroku Redis
if "REDIS_URL" in os.environ:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",  # Ensure django-redis is in requirements.txt
            "LOCATION": os.environ.get("REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": "redis://redis:6379",  # For local Docker setup
        }
    }

# If DEBUG is False, ensure SECURE_PROXY_SSL_HEADER is set for Heroku
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
