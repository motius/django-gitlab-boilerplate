from .base import *

DEBUG = False

ALLOWED_HOSTS = ["django-api.staging.motius.de"]

SITE_URL = 'http://django-api.staging.motius.de'
STATIC_URL = 'http://django-api.staging.motius.de/static/'

try:
    from .local import *
except ImportError:
    pass
