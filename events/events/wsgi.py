"""
WSGI config for events project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application
import os
import sys
sys.path.append("..")
from api.background_task import main

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'events.settings')

application = get_wsgi_application()
main()