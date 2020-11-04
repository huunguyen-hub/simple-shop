"""
WSGI config for spa project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys

sys.path.insert(0, '/home/huunguyen/.virtualenvs/pythonProject/lib/python3.9/site-packages/')

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spa.settings')

application = get_wsgi_application()
