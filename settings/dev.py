from .base import *

DEBUG=False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'vgrinfor_kolli_test',
        'USER': 'vgrinfor_admin',
        'PASSWORD': 'YqvyYGm5cJMLmzt',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        #'DEFAULT-CHARACTER-SET' : 'utf8',
        'OPTIONS': {
            # Tell MySQLdb to connect with 'utf8mb4' character set
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        # Tell Django to build the test database with the 'utf8mb4' character set
        'TEST': {
            'CHARSET': 'utf8mb4',
            'COLLATION': 'utf8mb4_unicode_ci',
        }
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_ROOT = '/home/vgrinfor/public_html/kodtjanst-dev/static'
STATICFILES_DIRS = ['/home/vgrinfor/kodtjanst-dev/static',]
STATIC_URL = '/kodtjanst-dev/static/'

# media files  - for where files are uploaded to
MEDIA_URL = '/kodtjanst-dev/media/'
MEDIA_ROOT = '/home/vgrinfor/public_html/kodtjanst-dev/media'

# Template directories
TEMPLATES[0]['DIRS'].append('templates/kodtjanst')


# Email settings

EMAIL_HOST = ''
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True