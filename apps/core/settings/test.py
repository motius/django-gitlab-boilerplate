from .base import *

DEBUG = False

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SITE_URL = 'http://127.0.0.1:8000'

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)


# Disables migrations,
class DisableMigrations(object):
    def __contains__(self, *args):
        return True

    def __getitem__(self, *args):
        return "notmigrations"


MIGRATION_MODULES = DisableMigrations()

