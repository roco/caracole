#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Django settings for floreal project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'some-random-set-of-ascii-characters'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
TEMPLATE_STRING_IF_INVALID = "[[[Invalid template variable %s]]]"
ALLOWED_HOSTS = []

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'XXXXXXXXXXXXXX'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = 'xxxxxxxxxxxx'
EMAIL_SUBJECT_PREFIX = 'xxxxxxxxxxxxxxx '

# longusernameandemail settings
MAX_USERNAME_LENGTH = 128
MAX_EMAIL_LENGTH = 128
REQUIRE_UNIQUE_EMAIL = False

# Application definition
DELIVERY_ARCHIVE_DIR = os.path.join(BASE_DIR, "deliveries")


INSTALLED_APPS = (
    'floreal',  # Before auth, so that app's password management templates take precedence
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',  # WARNING that's django-registration-redux, not django-registration!
    'longerusernameandemail', # sudo pip install django-longerusernameandemail
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'floreal.urls'

WSGI_APPLICATION = 'caracole.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/path/to/database.sqlite3'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_L10N = False
USE_TZ = True

LOGIN_URL = "/accounts/login"
LOGIN_REDIRECT_URL = "/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/caracole/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "floreal", "static"),
)

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
