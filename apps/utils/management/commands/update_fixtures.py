import json
import os
from io import StringIO

from django.apps.registry import apps
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Updates fixtures from the database'

    def handle(self, *args, **options):
        app_configs = [a for a in apps.get_app_configs() if a.name.startswith('apps.')]
        for app_config in app_configs:
            dirname = os.path.join(os.path.dirname(app_config.module.__file__), 'fixtures')
            filename = os.path.join(dirname, '{name}_data.json'.format(name=app_config.label))
            if not list(app_config.get_models()):
                continue
            models = ['{}.{}'.format(app_config.label, m._meta.object_name.lower()) for m in app_config.get_models() if m._meta.proxy is False]
            self.write_fixtures(filename, *models)

        self.write_fixtures(
            os.path.join(settings.BASE_DIR, 'user/fixtures/auth_data.json'),
            *['auth.user', 'auth.group', 'account']
        )

        self.write_fixtures(
            os.path.join(settings.BASE_DIR, 'core/fixtures/initial_data.json'),
            *['sites']
        )

    def write_fixtures(self, filename, *args):
        out = StringIO()
        print('Updating {filename}'.format(filename=filename))
        call_command('dumpdata', *args, stdout=out, natural_keys=True)
        parsed = json.loads(out.getvalue())

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        with open(filename, 'w') as fh:
            fh.write(json.dumps(parsed, indent=4, sort_keys=True))
