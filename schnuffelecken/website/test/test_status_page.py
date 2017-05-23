from django.test import TestCase, Client
from django.test.utils import setup_test_environment

from website.models import BookingPeriod

setup_test_environment()


class StatusPageTests(TestCase):

    def test_should_successfully_retrieve_status_for_facility_g(self):
        client = Client()

        response = client.get('/status/g/')

        calendar_week = BookingPeriod().weeks[0].calendar_week

        self.assertEqual(200, response.status_code)
        self.assertEqual(calendar_week, response.context["week"].calendar_week)

    def test_should_successfully_retrieve_status_for_facility_h(self):
        client = Client()

        response = client.get("/status/h/")

        calendar_week = BookingPeriod().weeks[0].calendar_week

        self.assertEqual(200, response.status_code)
        self.assertEqual(calendar_week, response.context["week"].calendar_week)

    def test_should_get_error_on_wrong_facility(self):
        client = Client()

        response = client.get("/status/x")

        self.assertEqual(404, response.status_code)

    def test_should_get_error_on_no_facility(self):
        client = Client()

        response = client.get("/status/")

        self.assertEqual(404, response.status_code)
