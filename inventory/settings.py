"""
Django settings for inventory project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

from decouple import config

# If the SENTRY_DSN env var is set, we enable the Django integration for Sentry
if config("SENTRY_DSN"):
    from sentry_sdk.integrations.django import DjangoIntegration
    import sentry_sdk

    sentry_sdk.init(dsn=config("SENTRY_DSN"), integrations=[DjangoIntegration()])


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGIN_URL = "/user/login/"
LOGIN_REDIRECT_URL = "/user/organizations"
LOGOUT_REDIRECT_URL = "/user/login/"

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config(
    "DJANGO_SECRET_KEY", default="_8+o1n6!8(5ooa!luo_7*x(qfgo!wyh-1hiu^zhg0u)b3)p_g5"
)


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG", cast=bool)

ALLOWED_HOSTS = ["localhost", "app.organization.supply", "127.0.0.1"]

# Application definition

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Installed apps
    "organizations",  # django-organizations (not to be confused with the one below)
    "rest_framework",  # Rest Framework is used for the API
    "rest_framework.authtoken",  # API key access
    "import_export",  # Import export functionality
    # Apps
    "organization.apps.OrganizationConfig",  # Main application for inventory
    "user.apps.UserConfig",  # User pages and settings
    "api.apps.ApiConfig",  # REST API
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "inventory.middleware.OrganizationMiddleware",
]

ROOT_URLCONF = "inventory.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

AUTH_USER_MODEL = (
    "user.User"
)  # Custom user model that has email/password instead of username/email/password

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
}

ORGS_SLUGFIELD = "django_extensions.db.fields.AutoSlugField"

NOTIFICATIONS_NOTIFICATION_MODEL = "organization.InventoryNotification"

WSGI_APPLICATION = "inventory.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
if config("POSTGRES_ENABLED", default=False, cast=bool):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": config("POSTGRES_DB"),
            "USER": config("POSTGRES_USER"),
            "PASSWORD": config("POSTGRES_PASSWORD"),
            "HOST": config("POSTGRES_HOST", default="localhost"),
            "PORT": config("POSTGRES_PORT", default=5432, cast=int),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Email configuration (sendgrid)

SENDGRID_API_KEY = config("SENDGRID_API_KEY")

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = SENDGRID_API_KEY
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "notifications@organization.supply"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATICFILES_DIRS = [os.path.join(BASE_DIR, "identity/")]
STATIC_URL = "/static/"
STATIC_ROOT = config("DJANGO_STATIC_ROOT", default=os.path.join(BASE_DIR, "static/"))

MEDIA_URL = "/media/"
MEDIA_ROOT = config("DJANGO_MEDIA_ROOT", default=os.path.join(BASE_DIR, "media/"))
