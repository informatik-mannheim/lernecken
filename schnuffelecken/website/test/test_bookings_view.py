from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory, Client
from django.test.utils import setup_test_environment
from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta

from website.models import *
from ..viewmodels import *


setup_test_environment()


def create_test_booking(user, date, time, facility='g'):
    date = datetime(date.year, date.month, date.day, time)
    booking = Booking(date=date, user=user.username, facility='g')
    booking.save()

    return booking


class BookingsViewTests(TestCase):

    def setUp(self):
        """
        Create two users and log one of them in.
        Determine the current week and the first day of it.
        """
        self.client = Client()

        self.user = User.objects.get_or_create(
            username='max', first_name="Max", last_name="Mustermann")[0]
        self.someone = User.objects.get_or_create(
            username='peter', first_name="Peter", last_name="Müller")[0]

        self.client.force_login(self.user)
        self.facility = 'g'

        self.current_week = BookingPeriod().weeks[0]
        self.first_day = self.current_week.start

        now = datetime.now()
        self.today = datetime(
            year=now.year, month=now.month, day=now.day, hour=8)

    def test_should_display_default_values(self):
        """
        Should display username, quota and the first week bookings table
        """
        response = self.client.get(
            reverse('bookings', kwargs={'facility': 'g'}))

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 200)

        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA)
        self.assertEqual(context["display_first_week"], True)
        self.assertEqual(context["is_g"], True)

        self.assertEqual(bookings[0].calendar_week,
                         self.current_week.calendar_week)
        self.assertEqual(bookings[1].calendar_week,
                         self.current_week.calendar_week + 1)
        self.assertEqual(bookings[2].calendar_week,
                         self.current_week.calendar_week + 2)
        self.assertEqual(bookings[3].calendar_week,
                         self.current_week.calendar_week + 3)

    def test_should_display_selected_facility(self):
        """
        Should hightlight facility h if h is selcted
        """
        response = self.client.get(
            reverse('bookings', kwargs={'facility': 'h'}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["is_g"], False)

    def test_should_not_display_facility_other_than_g_or_h(self):
        """
        Should hightlight facility h if h is selcted
        """
        response = self.client.get("/buchungen/x")

        self.assertEqual(response.status_code, 404)

    def test_all_available(self):
        """
        Should display all blocks as available if nothing was booked
        """
        response = self.client.get(
            reverse('bookings', kwargs={'facility': 'g'}))

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 200)

        self.assertEqual(context["username"], self.user)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA)
        self.assertEqual(context["display_first_week"], True)

        self.assertEqual(bookings[0].calendar_week,
                         self.current_week.calendar_week)
        self.assertEqual(bookings[1].calendar_week,
                         self.current_week.calendar_week + 1)
        self.assertEqual(bookings[2].calendar_week,
                         self.current_week.calendar_week + 2)
        self.assertEqual(bookings[3].calendar_week,
                         self.current_week.calendar_week + 3)

        for week in bookings:
            for row in week.rows:
                for block in row.blocks:
                    self.assertEqual(type(block), BlockAvailable)

    def test_one_reserveation(self):
        """
        Should display one block as reserved, all others as available
        """
        test_booking = create_test_booking(self.user, self.first_day, 11)

        response = self.client.get(
            reverse('bookings', kwargs={'facility': 'g'}))

        bookings = response.context["bookings"]

        for week in bookings:
            for row in week.rows:
                for block in row.blocks:
                    if block.date == test_booking.date:
                        self.assertEqual(type(block), BlockReserved)
                    else:
                        self.assertEqual(type(block), BlockAvailable)

    def test_one_reserveation_and_one_booked(self):
        """
        Should display one block as reserved, one as booked, all others as available
        """
        own_booking = create_test_booking(self.user, self.first_day, 11)
        other_booking = create_test_booking(self.someone, self.first_day, 12)

        response = self.client.get(
            reverse('bookings', kwargs={'facility': 'g'}))
        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA - 1)

        for week in bookings:
            for row in week.rows:
                for block in row.blocks:
                    if block.date == own_booking.date:
                        self.assertEqual(type(block), BlockReserved)
                    elif block.date == other_booking.date:
                        self.assertEqual(type(block), BlockBooked)
                    else:
                        self.assertEqual(type(block), BlockAvailable)

    def test_make_a_booking(self):
        """
        The user should be able to make a booking
        """
        date = datetime(2030, 3, 1, 11)

        response = self.client.post(reverse('bookings', kwargs={'facility': 'g'}), {
                                    'book': str(date.timestamp())})

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA - 1)
        self.assertEqual(type(context["info"]), BookingSuccessfulAlert)

        for week in bookings:
            for row in week.rows:
                for block in row.blocks:
                    if block.date == date:
                        self.assertEqual(type(block), BlockReserved)
                    else:
                        self.assertEqual(type(block), BlockAvailable)

    def test_cancel_booking(self):
        """
        The user should be able to cancel a booking he made previously
        """
        date = datetime(2060, 3, 1, 11)

        booking = create_test_booking(self.user, date, date.hour)

        response = self.client.post(
            reverse('bookings', kwargs={'facility': 'g'}), {'cancel': str(date.timestamp())})

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA)
        self.assertEqual(type(context["info"]), CancellationAlert)

        for week in bookings:
            for row in week.rows:
                for block in row.blocks:
                    self.assertEqual(type(block), BlockAvailable)

    def test_can_not_reserve_booked_block(self):
        """
        The user should not be able to book an already booked block
        """
        booking_other = create_test_booking(self.someone, self.first_day, 11)

        response = self.client.post(
            reverse('bookings', kwargs={'facility': 'g'}), {'book': str(booking_other.date.timestamp())})

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 403)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA)

        self.assertEqual(type(context["info"]), NotAllowedAlert)

    def test_can_not_exceed_quota(self):
        """
        The user should not be able to create more bookings than his quota allows (across facilities)
        """
        create_test_booking(self.user, self.first_day, 8, facility='g')
        create_test_booking(self.user, self.first_day, 9, facility='0')
        create_test_booking(self.user, self.first_day, 10, facility='g')
        create_test_booking(self.user, self.first_day, 11, facility='h')
        create_test_booking(self.user, self.first_day, 12, facility='h')
        create_test_booking(self.user, self.first_day, 13, facility='g')
        create_test_booking(self.user, self.first_day, 14, facility='x')
        create_test_booking(self.user, self.first_day, 15, facility='y')
        create_test_booking(self.user, self.first_day, 16, facility='g')
        create_test_booking(self.user, self.first_day, 17, facility='g')

        date = datetime(2030, 1, 1, 8)

        response = self.client.post(
            reverse('bookings', kwargs={'facility': 'g'}), {'book': str(date.timestamp())})

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 403)
        self.assertEqual(context["quota"], 0)
        self.assertEqual(type(context["info"]), QuotaExceededAlert)

    def test_past_bookings_do_not_affect_quota(self):
        """
        The user quota should not reflect bookings in the past (that are already finished)
        """
        long_ago = datetime(1990, 12, 1)
        last_week = self.today - timedelta(7)

        create_test_booking(self.user, long_ago, 8)
        create_test_booking(self.user, last_week, 18)

        response = self.client.get(
            reverse('bookings', kwargs={'facility': 'g'}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["quota"], settings.BOOKINGS_QUOTA)

    def test_only_display_bookings_for_selected_facility(self):
        """
        Should display bookings for selected facility
        """
        booking = create_test_booking(
            self.user, self.first_day, 8, facility='g')

        response = self.client.get(
            reverse('bookings', kwargs={'facility': 'g'}))

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA - 1)

        for week in bookings:
            for row in week.rows:
                for block in row.blocks:
                    if block.date == booking.date:
                        self.assertEqual(type(block), BlockReserved)
                    else:
                        self.assertEqual(type(block), BlockAvailable)

    def test_do_not_show_bookings_from_unselected_facility(self):
        """
        Should not display bookings from another facility
        """
        booking = create_test_booking(
            self.user, self.first_day, 8, facility='g')

        response = self.client.get(
            reverse('bookings', kwargs={'facility': 'h'}))

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA - 1)

        for week in bookings:
            for row in week.rows:
                for block in row.blocks:
                    self.assertEqual(type(block), BlockAvailable)

    def test_can_not_book_running_block(self):
        """
        Client can not book the block that is currently running
        """
        date = datetime.now().replace(minute=0, second=0, microsecond=0)

        response = self.client.post(
            reverse('bookings', kwargs={'facility': 'g'}), {'book': str(date.timestamp())})

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 403)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA)

    def test_can_not_book_past_block(self):
        """
        Client can not book the block that is currently running
        """
        date = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

        response = self.client.post(
            reverse('bookings', kwargs={'facility': 'g'}), {'book': str(date.timestamp())})

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 403)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA)

    def test_can_not_cancel_current_block(self):
        """
        Client can not cancel the block that is currently running
        """
        date = datetime.now().replace(minute=0, second=0, microsecond=0)

        response = self.client.post(
            reverse('bookings', kwargs={'facility': 'g'}), {'cancel': str(date.timestamp())})

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 403)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA)

    def test_can_not_cancel_past_block(self):
        """
        Client can not cancel a past block
        """
        date = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

        response = self.client.post(
            reverse('bookings', kwargs={'facility': 'g'}), {'cancel': str(date.timestamp())})

        context = response.context
        bookings = context["bookings"]

        self.assertEqual(response.status_code, 403)
        self.assertEqual(context["quota"], settings.BOOKINGS_QUOTA)
