from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UtilsConfig(AppConfig):
    name = 'apps.utils'
    verbose_name = _('Utilities')
