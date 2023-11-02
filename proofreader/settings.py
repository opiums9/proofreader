"""
Django settings for proofreader project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

import os
import sys
from pathlib import Path

import environ
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
env.read_env(str(BASE_DIR / 'config.env'))

SECRET_KEY = "django-insecure-w$z((s_-9p#@o7qhdppz6!&_$nsh)_=%o0*$++auotml^ns+8z"

DEBUG = env.bool('DEBUG', default=True)

LOCAL_DEVELOP = DEBUG and (
    'runserver' in sys.argv or 'pydevconsole' in sys.argv[0]  # run locally  # run from console locally
)
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "crispy_forms",
    "crispy_bootstrap5",
    "tz_detect",
    'django_celery_beat',
    'django_celery_results',
    'simple_history',
    # This project
    "books.apps.BooksConfig",
    "accounts.apps.AccountsConfig",
]

INSTALLED_APPS += ['taskapp.celery.CeleryAppConfig']

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 3rd party
    "tz_detect.middleware.TimezoneMiddleware",
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = "proofreader.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'core.context_processors.custom_settings',
            ],
        },
    },
]

WSGI_APPLICATION = "proofreader.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {
    "default": {
        **env.db('DATABASE_URL', default='db://postgres:postgres@db:5432/postgres'),
        "ENGINE": "django.db.backends.postgresql",
        "OPTIONS": {"options": "-c search_path=django"},
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_REDIRECT_URL = "book_list"
LOGOUT_REDIRECT_URL = "/home"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

AUTH_USER_MODEL = "accounts.CustomUser"

# Celery
# ------------------------------------------------------------------------------
# http://docs.celeryproject.org/en/latest/userguide/configuration.html
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://guest:guest@localhost:5672/')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERYD_TASK_TIME_LIMIT = 60
CELERYD_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
worker_proc_alive_timeout = 60
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_EXPIRES = 60 * 60 * 24 * 7

REDIS_URL = env('REDIS_URL', default='redis://redis:6379/1')

# Media files
MEDIA_URL = env('DJANGO_MEDIA_URL', default='/media/')
MEDIA_ROOT = str(BASE_DIR / 'media')

FILE_UPLOAD_PERMISSIONS = 0o644

if env.bool('LOCAL', default=False):
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
    CELERY_TASK_ALWAYS_EAGER = True
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-eager-propagates
    CELERY_TASK_EAGER_PROPAGATES = True

sentry_sdk.set_tag("server", 'develop' if DEBUG else 'production')
if sentry_dsn := env("SENTRY_DSN", default=''):
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=0.1,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        send_default_pii=True,
    )

# Admin styles for different environments:
if LOCAL_DEVELOP:
    ADMIN_SETTINGS = {'title': 'Proofreader Local', 'header_color': '#000000', 'breadcrumbs_color': '#e81a9b'}
elif DEBUG:
    ADMIN_SETTINGS = {'title': 'Proofreader DEV', 'header_color': '#53ab70', 'breadcrumbs_color': '#206d22'}
else:
    ADMIN_SETTINGS = {'title': 'Proofreader', 'header_color': '#fd5e60', 'breadcrumbs_color': '#e8736a'}

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
