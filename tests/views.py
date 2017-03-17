import json
import logging

from django.contrib.auth import get_user_model
from hamcrest import assert_that, has_key

from django.core.urlresolvers import reverse

from apps.core.urls import router
from libs.tests import BaseAPITestCase
from tests.recipes import UserRecipe
from .recipes import EmailAddressRecipe

log = logging.getLogger(__name__)


class TestAPIResponses(BaseAPITestCase):
    """
    Smoke test to see if (almost) all api views work.
    """
    # Overwrite args for detail routes that do not use an id
    detail_args = {}
    ignore_urls = ['api-root']

    def setUp(self):
        super().setUp()
        urls = set(list([u.name for u in router.get_urls()]))
        self.default_viewset_urls = []
        self.extra_urls = []

        for u in urls:
            if u in self.ignore_urls:
                continue
            u = 'api:{}'.format(u)
            if u.endswith('-detail') or u.endswith('-list'):
                self.default_viewset_urls.append(u)
            else:
                self.extra_urls.append(u)

    def test_default_viewset_reponses(self):
        for name in self.default_viewset_urls:
            if name.endswith('-detail'):
                args = self.detail_args[name] if name in self.detail_args else [1]
                url = reverse(name, args=args)
            else:
                url = reverse(name)

            if name.endswith('-list'):
                self.assert_url_list_not_empty(url)
            else:
                self.get_200_response(url)

    def test_extra_viewset_reponses(self):
        no_list_urls = []
        urls = self.extra_urls
        for name in urls:
            url = reverse(name)
            if name in no_list_urls:
                self.get_200_response(url)
            else:
                self.assert_url_list_not_empty(url)

    def test_standalone_responses(self):
        urls = []

        for url in urls:
            self.get_200_response(url)

    def test_token_login(self):
        data = dict(username="bar", password="bar")
        user = get_user_model().objects.create_user(**data)
        EmailAddressRecipe.make(user=user, verified=True)
        url = reverse('rest_login')
        response = self.client.post(url, data)
        assert_that(json.loads(response.content.decode("utf8")),
                    has_key("token"))
