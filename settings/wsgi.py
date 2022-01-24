"""
WSGI config for kodtjänst project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys
import socket
import logging
logger = logging.getLogger(__name__)

from django.core.wsgi import get_wsgi_application

if socket.gethostname() == 'suijin.oderland.com':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if 'dev' in dir_path:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.dev')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

application = get_wsgi_application()
