import ldap
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = [
    'localhost',
    'lernecken.hs-mannheim.de',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'website.apps.WebsiteConfig',
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

ROOT_URLCONF = 'schnuffelecken.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'website/templates/website')],
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

WSGI_APPLICATION = 'schnuffelecken.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

AUTHENTICATION_BACKENDS = [
    # authenticate employees and students (frontend)
    'django_auth_ldap.backend.LDAPBackend',
    # authenticate superuser (backend)
    'django.contrib.auth.backends.ModelBackend',
]


# log out user automatically after n seconds by deleting session cookie
SESSION_COOKIE_AGE = 3600

# LDAP-specific settings
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_DEBUG_LEVEL: 0,
    ldap.OPT_REFERRALS: 0,
}

AUTH_LDAP_START_TLS = True

# Localization settings
LANGUAGE_CODE = 'DE'
TIME_ZONE = 'CET'
USE_TZ = False
USE_I18N = False
USE_L10N = False

# Static files
STATIC_URL = '/static/'

STATICFILES_DIRs = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Bookings quota per user (total for the next 4 weeks and both lernecken)
BOOKINGS_QUOTA = 10

# limit access to students only by settings STAFF_ACCESS = False
STAFF_ACCESS = False

# in production, ALWAYS set this to False
DEBUG = False

# every 24 hours, bookings older than this value will be removed
OLD_BOOKINGS_EXPIRATION_IN_DAYS = 30

# how often the status page should be refreshed when displayed, in seconds
STATUS_PAGE_REFRESH_RATE_IN_SECONDS = 30

# full URL of where the system is deployed (displayed in footer of status page)
URL = "https://lernecken.hs-mannheim.de"

# put this in the end so it allows for local overrides in settings_secret.py
from .settings_secret import *
