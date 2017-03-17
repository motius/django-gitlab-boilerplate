from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FrontendConfig(AppConfig):
    name = 'apps.frontend'
    verbose_name = _('Frontend')
