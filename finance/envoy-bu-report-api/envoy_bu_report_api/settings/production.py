# production.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Additional production settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
