from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.utils import setup_test_environment
from django.utils import timezone

from datetime import datetime, timedelta
from website.models import *
from website.viewmodels import WeekViewModel

setup_test_environment()


class BookingPeriodTests(TestCase):

    def setUp(self):
        self.user = User.objects.get_or_create(
            username='max', first_name="Max", last_name="Mustermann")[0]

    def test_period_always_starts_on_a_monday(self):
        """
        No matter what date is provided, a week should always start on a monday.
        If the date is a saturday or sunday, it seeks the next monday, otherwise the last.
        """
        monday = datetime(2017, 3, 27)
        tuesday = datetime(2017, 3, 28)
        wednesday = datetime(2017, 3, 29)
        thursday = datetime(2017, 3, 30)
        friday = datetime(2017, 3, 31)
        saturday = datetime(2017, 4, 1)
        sunday = datetime(2017, 4, 2)

        next_monday = datetime(2017, 4, 3)

        self.assertEqual(BookingPeriod(monday).start, monday)
        self.assertEqual(BookingPeriod(tuesday).start, monday)
        self.assertEqual(BookingPeriod(wednesday).start, monday)
        self.assertEqual(BookingPeriod(thursday).start, monday)
        self.assertEqual(BookingPeriod(friday).start, monday)
        self.assertEqual(BookingPeriod(saturday).start, next_monday)
        self.assertEqual(BookingPeriod(sunday).start, next_monday)

    def test_period_is_based_on_today_if_no_date_provided(self):
        """
        A BookingPeriod should calculate it's start date relative to today if no 
        start date was provided.
        """
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if today.weekday() < 5:
            monday = today - timedelta(today.weekday())
        else:
            monday = today + timedelta(7 - today.weekday())

        booking_period = BookingPeriod()

        self.assertEqual(booking_period.start, monday)

    def test_period_always_has_four_weeks(self):
        """
        A booking period should always consist of four weeks.
        """
        start = datetime(2017, 3, 27)

        weeks = BookingPeriod(start).weeks

        self.assertEqual(len(weeks), 4)

    def test_period_weeks_start_with_mondays(self):
        """
        A BookingPeriod should always have a monday as start date and four successive
        weeks from that monday, even if the provided date was not a monday.
        """
        monday = datetime(2017, 3, 27)
        thursday = datetime(2017, 3, 30)

        weeks = BookingPeriod(date=thursday).weeks

        self.assertEqual(weeks[0].start, monday)
        self.assertEqual(weeks[1].start, monday + timedelta(7))
        self.assertEqual(weeks[2].start, monday + timedelta(14))
        self.assertEqual(weeks[3].start, monday + timedelta(21))

    def test_week_has_five_successive_days_starting_monday(self):
        """
        A week should always consist of 5 days, starting on a monday.
        The week does NOT perform a check whether the supplied date is a monday.
        """
        monday = datetime(2017, 3, 27)

        week = Week(start=monday)

        self.assertEqual(week.start, monday)
        self.assertEqual(len(week.days), 5)

        self.assertEqual(week.days[0].date, monday)
        self.assertEqual(week.days[1].date, monday + timedelta(1))
        self.assertEqual(week.days[2].date, monday + timedelta(2))
        self.assertEqual(week.days[3].date, monday + timedelta(3))
        self.assertEqual(week.days[4].date, monday + timedelta(4))

    def test_day_can_get_all_bookings_per_user_and_facility(self):
        """
        A day should fetch a list of available / booked / reserved blocks for a given
        combination of date, user and facility
        """
        monday = datetime(2017, 3, 27, 18)
        monday_at_eight_am = datetime(2017, 3, 27, 8)
        monday_at_nine_am = datetime(2017, 3, 27, 9)
        monday_at_ten_am = datetime(2017, 3, 27, 10)
        monday_at_noon = datetime(2017, 3, 27, 12)
        monday_at_three_pm = datetime(2017, 3, 27, 15)
        friday_at_eight_am = datetime(2017, 3, 31, 8)

        Booking(date=monday_at_eight_am,
                user=self.user.username, facility='h').save()
        Booking(date=monday_at_nine_am,
                user=self.user.username, facility='g').save()
        Booking(date=monday_at_ten_am, user='jakob', facility='g').save()
        Booking(date=monday_at_noon, user='ute', facility='g').save()
        Booking(date=monday_at_three_pm,
                user=self.user.username, facility='g').save()
        Booking(date=friday_at_eight_am, user='jon', facility='x').save()

        bookings = Day(monday).get_bookings('g', self.user)

        self.assertEqual(len(bookings), 11)

        self.assertEqual(type(bookings[0]), BlockAvailable)
        self.assertEqual(type(bookings[1]), BlockReserved)
        self.assertEqual(type(bookings[2]), BlockBooked)
        self.assertEqual(type(bookings[3]), BlockAvailable)
        self.assertEqual(type(bookings[4]), BlockBooked)  # by ute
        self.assertEqual(type(bookings[5]), BlockAvailable)
        self.assertEqual(type(bookings[6]), BlockAvailable)
        self.assertEqual(type(bookings[7]), BlockReserved)  # by max
        self.assertEqual(type(bookings[8]), BlockAvailable)
        self.assertEqual(type(bookings[9]), BlockAvailable)
        self.assertEqual(type(bookings[10]), BlockAvailable)