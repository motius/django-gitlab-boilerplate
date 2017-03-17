import logging
from io import StringIO
from unittest.case import skip

from django.core.management import call_command
from django.test.utils import override_settings
from django.apps import apps
from django.core.urlresolvers import reverse
from django.test import TestCase

from libs.tests import BaseAPITestCase

log = logging.getLogger(__name__)


@skip
class CreateModelSmokeTest(BaseAPITestCase):
    """
    TODO: Implement a model create test case
    """
    def test_create_with_api(self):
        pc = YourModel.make()
        url = reverse('yourmodel-list', kwargs=dict(photochallenge_pk=pc.pk))
        response = self.client.post(url, dict(title='title'))
        self.assert_status_code(response, 201)


class ModelStringifyTestCase(TestCase):
    """
    Call str() of all our models. Should not fail for (un)saved records.
    """
    def test_model_str_methods(self):
        models = [m for m in apps.get_models()
                  if m._meta.model.__module__.startswith("apps.")]
        for M in models:
            # Unsaved record:
            str(M())
            # Existing record:
            if M.objects.exists():
                str(M.objects.all()[0])


class TestMissingMigrations(TestCase):
    @override_settings(MIGRATION_MODULES={})
    def test_for_missing_migrations(self):
        output = StringIO()
        try:
            call_command('makemigrations', interactive=False, dry_run=True, exit_code=True, stdout=output)
        except SystemExit as e:
            # The exit code will be 1 when there are no missing migrations
            self.assertEqual(str(e), '1', 'makemigrations exit code indicates there are missing migrations')
        else:
            self.fail("There are missing migrations:\n %s" % output.getvalue())
