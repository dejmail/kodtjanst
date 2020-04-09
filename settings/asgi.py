"""
ASGI config for kodtjänst project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
import sys
import socket

from django.core.asgi import get_asgi_application

if socket.gethostname() == 'suijin.oderland.com':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

application = get_asgi_application()
