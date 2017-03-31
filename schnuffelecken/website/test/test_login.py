from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.test.utils import setup_test_environment
from django.urls import reverse

setup_test_environment()


class LoginViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.username = settings.TEST_USER_NAME
        self.password = settings.TEST_USER_PASS

    def test_login_page(self):
        """
        Should display plain login page
        """
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue("message" not in response.context)

    def test_redirect_unauthenticated_user_to_login_page(self):
        """
        For convenience, redirect requests to root URL to the login page
        """
        response = self.client.get('/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))

    def test_redirect_authenticated_user_to_bookings_page(self):
        """
        For convenience, redirect requests to root URL to the login page
        """
        self.client.login(username=self.username, password=self.password)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('bookings', kwargs={"facility":"g"}))

        self.client.logout()

    def test_redirect_to_login_page_on_restricted_page(self):
        """
        Redirect to login page if trying to make unauthenicated bookings
        """
        response = self.client.get(reverse('bookings', args=["g"]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login/?next=/buchungen/g/')

    def test_successful_login(self):
        """
        Redirect to bookings page on successful login
        """
        response = self.client.post(
            '/login/', {'username': self.username, 'password': self.password})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/buchungen/g/")

    def test_invalid_login(self):
        """
        Do not allow invalid logins (wrong combination of username and password)
        """
        response = self.client.post(
            '/login/', {'username': 'not_existing', 'password': 'xxxxx'})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.context['error'], 'Konto nicht gefunden')

    @override_settings(STAFF_ACCESS=False)
    def test_no_access_for_employees(self):
        """
        Do not allow employees to log in if settings.STAFF_ACCESS = False
        """

        response = self.client.post(
            '/login/', {'username': self.username, 'password': self.password})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.context['error'], 'Für Mitarbeiter gesperrt')

    @override_settings(STAFF_ACCESS=False)
    def test_still_allowed_for_students(self):
        response = self.client.post(
            '/login/', {'username': '999999', 'password': 'xxxxx'})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.context['error'], 'Konto nicht gefunden')
