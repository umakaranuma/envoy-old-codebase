# settings/__init__.py
import os
from django.core.exceptions import ImproperlyConfigured
from .base import *
ENV = os.getenv( 'development','production')

if ENV == 'development':
    from .development import *
elif ENV == 'production':
    from .production import *
else:
    raise ImproperlyConfigured(f"Unknown DJANGO_ENV: {ENV}")
