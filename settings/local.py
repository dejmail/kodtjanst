from .base import *
import os 
import logging

logger = logging.getLogger(__name__)

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME' : 'kodverk_databas.sqlite3'
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'vgrinfor_kodtjanst_backup',
        'USER': 'vgrinfor_admin',
        'PASSWORD': 'YqvyYGm5cJMLmzt',
        'HOST': 'suijin.oderland.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        #'DEFAULT-CHARACTER-SET' : 'utf8',
        'OPTIONS': {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            'charset': 'utf8mb4',
        },
        # Tell Django to build the test database with the 'utf8mb4' character set
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
logger.info(f'PROJECT_PATH --> {PROJECT_PATH}')

TEMPLATES[0]['DIRS'].append('templates/kodtjanst')


STATICFILES_DIRS = [
    "static",
    '/mnt/c/Users/liath1/coding/kodtjänst/static/',
]
#STATIC_ROOT = '/mnt/c/Users/liath1/coding/kodtjänst/static'
STATIC_URL = '/static/'

# Email settings
# Use this backend if you want the system to print out emails to the console
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'mail.vgrinformatik.se'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'info@vgrinformatik.se'
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True