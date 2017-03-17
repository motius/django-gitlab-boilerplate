import logging
from collections import OrderedDict

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework.utils.serializer_helpers import ReturnList
from hamcrest import (assert_that, greater_than, instance_of, any_of,
                      is_, is_in, has_key, has_length)

from tests.recipes import EmailAddressRecipe

log = logging.getLogger(__name__)


class LoginAPITestCase(APITestCase):
    def login(self):
        data = dict(email="foo@bar.com", password="foo")
        user = get_user_model().objects.create_user(username="foo", is_staff=True, is_superuser=True, **data)
        EmailAddressRecipe.make(user=user, verified=True)
        self.client.login(**data)


class BaseAPITestCase(LoginAPITestCase):
    fixtures = [
        'apps/user/fixtures/auth_data.json',
    ]

    def setUp(self):
        EmailAddressRecipe.make(user=get_user_model().objects.get(pk=1), verified=True)  # Verify admin
        # Create user to log in as
        self.login()
        self.api_factory = APIRequestFactory(format='json')

    def assert_status_code(self, response, status_code):
        self.assertEqual(response.status_code, status_code, 'Wrong status code on {url}: {data}'.format(
            url=response.request.get('PATH_INFO'),
            data=response.data,
        ))

    def assert_url_list_length(self, url, length):
        response = self.get_200_response(url)
        assert_that(response.data, has_length(length), url)

    def assert_url_list_not_empty(self, url):
        """
        Ensure we have at least one record as empty lists would not engage
        serializer.
        """
        response = self.get_200_response(url)
        try:
            assert_that(response.data, any_of(instance_of(OrderedDict),
                                              instance_of(ReturnList),
                                              instance_of(list)))
            assert_that(len(response.data), greater_than(0))
        except:
            log.info("Expected non-empty list as result from {}".format(url))
            raise

    def assert_400_with_validation_error(self, response, msg, key="non_field_errors"):
        self.assert_status_code(response, 400)
        data = response.data
        assert_that(data, has_key(key))
        assert_that(data[key], has_length(1))
        self.assertEqual(data[key][0], msg)

    def get_200_response(self, url):
        """Grab url, assert 200 status code and return response."""
        try:
            response = self.client.get(url)
        except:
            log.info("{} failed.".format(url))
            raise
        self.assert_status_code(response, 200)
        log.info("{}   200".format(url))
        return response


class SerializerSmokeTestCaseMixin(LoginAPITestCase):
    """
    Tests modelviewset with given sample data:
    - creating new record via api
    - updating record via api
    - serialize/deserialize record
    Making this a mixin as we don't want it to run by itself
    Introduced after an innocent looking fields definition on a serializer worked
    well for reading but not for writing.
    """

    def setUp(self):
        super().setUp()
        self.login()
        self.model = self.ViewsetClass.queryset.model
        self.model.objects.all().delete()  # get rid of dummy_data.json
        self.list_url = reverse("api:{}-list".format(self.model.__name__.lower()))
        self.detail_url = "api:{}-detail".format(self.model.__name__.lower())
        self.serializer_class = self.get_serializer_class()

    def get_serializer_class(self):
        request = self.api_factory.post(self.list_url)
        viewset = self.ViewsetClass()
        viewset.request = request
        viewset.format_kwarg = "json"
        return viewset.get_serializer_class()

    def create_from_sample_data_via_api(self):
        return self.client.post(self.list_url, self.sample_data)

    def create_empty_via_api(self):
        return self.client.post(self.list_url, {})

    def test_empty_instance_does_not_fail_serializer(self):
        print(self.serializer_class(self.model()).data)

    def test_empty_input_does_not_raise_500(self):
        """
        Ensure empty/unsaved data does not raise 500s in serializer.
        """
        response = self.create_empty_via_api()
        assert_that(response.status_code, is_in([201, 400]))

    def test_can_create_record_via_viewset_api_endpoint(self):
        response = self.create_from_sample_data_via_api()
        if not response.status_code == 201:
            log.error(response.content)
        self.assert_status_code(response, 201)

    def test_can_update_record_via_viewset_api_endpoint(self):
        self.create_from_sample_data_via_api()
        pk = self.ViewsetClass.queryset.model.objects.get().pk
        response = self.client.patch(reverse(self.detail_url, args=[pk]),
                                     self.update_data)
        if not response.status_code == 200:
            log.error(response.content)
        self.assert_status_code(response, 200)
        key, value = self.update_data.popitem()
        data_value = response.data.get(key)
        # API might respond with a dict containing the sent ID
        if data_value != value and isinstance(data_value, dict) and 'id' in data_value:
            assert_that(data_value['id'], is_(value))
        else:
            assert_that(data_value, is_(value))

    def test_viewset_serializer_validates_does_not_fail_on_optional_fields(self):
        """
        Regression test for serializer classes
        """
        serializer = self.serializer_class(data=self.sample_data)
        serializer.is_valid(raise_exception=True)
