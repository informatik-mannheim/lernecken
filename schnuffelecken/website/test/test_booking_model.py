from django.conf import settings
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import setup_test_environment
from django.db.utils import IntegrityError

from datetime import datetime, timedelta

from ..models import *

setup_test_environment()


class BookingModelTests(TestCase):

    def setUp(self):
        now = datetime.now()
        self.today = datetime(
            year=now.year, month=now.month, day=now.day, hour=8)

    def test_delete_nothing_if_no_bookings(self):
        """
        If there is nothing, delete nothing
        """
        removed_bookings = Booking.remove_old()
        bookings_left = Booking.objects.all()

        self.assertEqual(removed_bookings, 0)
        self.assertEqual(len(bookings_left), 0)

    def test_do_not_delete_recent_bookings(self):
        """
        Do not delete recent bookings (newer than 30 days in the past)
        """

        yesterday = self.today - timedelta(1)
        day_before_yesterday = self.today - timedelta(2)
        twenty_nine_days_ago = self.today - timedelta(29)

        Booking(date=self.today, user="max", facility='h').save()
        Booking(date=yesterday, user="sabine", facility='h').save()
        Booking(date=day_before_yesterday, user="heinz", facility='h').save()
        Booking(date=twenty_nine_days_ago,
                user="stefanie", facility='h').save()

        removed_bookings = Booking.remove_old()
        bookings_left = Booking.objects.all()

        self.assertEqual(removed_bookings, 0)
        self.assertEqual(len(bookings_left), 4)

    def test_delete_bookings_older_than_thirty_days(self):
        """
        Delete bookings older than 30 days
        """

        today = self.today
        yesterday = today - timedelta(1)
        thirty_days_ago = today - timedelta(30)
        thirty_one_days_ago = today - timedelta(31)
        thirty_two_days_ago = today - timedelta(32)
        sixty_days_ago = today - timedelta(60)
        thousand_days_ago = today - timedelta(1000)

        # these should stay
        Booking(date=today, user="max", facility='h').save()
        Booking(date=yesterday, user="sabine", facility='h').save()
        Booking(date=thirty_days_ago, user="maria", facility='h').save()

        # these should be removed
        Booking(date=thirty_one_days_ago, user="stefanie", facility='h').save()
        Booking(date=sixty_days_ago, user="karl", facility='h').save()
        Booking(date=thousand_days_ago, user="stefanie", facility='h').save()

        removed_bookings = Booking.remove_old()
        bookings_left = Booking.objects.all()

        self.assertEqual(removed_bookings, 3)
        self.assertEqual(len(bookings_left), 3)

    def test_delete_old_bookings_and_accumulate_them(self):
        """
        After removing old bookings, also accumulate them
        """
        monday = datetime(2014, 1, 27, 8)

        kw5_2014 = [
            Booking(date=monday, user="max", facility='h'),
            Booking(date=(monday + timedelta(1)), user="max", facility='h'),
            Booking(date=(monday + timedelta(2)), user="max", facility='h'),
            Booking(date=(monday + timedelta(3)), user="max", facility='h'),
            Booking(date=(monday + timedelta(4)), user="max", facility='h'),
        ]

        [booking.save() for booking in kw5_2014]

        removed_bookings = Booking.remove_old()
        bookings_left = Booking.objects.count()

        self.assertEqual(5, removed_bookings)
        self.assertEqual(0, bookings_left)

        self.assertEqual(1, Statistic.objects.count())
        self.assertEqual(5, Statistic.objects.get(
            calendar_week=5, year=2014, facility='h').bookings)

    def test_do_not_allow_empty_user_name_on_clean(self):
        booking = Booking(date=datetime(2017, 1, 3, 12))
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_do_not_allow_bookings_with_minutes(self):
        booking = Booking(date=datetime(2017, 1, 3, 12, 1, 0, 0), user="max")

        with self.assertRaisesRegexp(ValidationError, 'Time must contain only full hours'):
            booking.clean()

    def test_do_not_allow_bookings_with_seconds(self):
        booking = Booking(date=datetime(2017, 1, 3, 12, 0, 1, 0), user="max")

        with self.assertRaisesRegexp(ValidationError, 'Time must contain only full hours'):
            booking.clean()

    def test_do_not_allow_booking_outside_business_hours(self):
        too_early = Booking(date=datetime(2017, 1, 3, 7), user="max")
        too_late = Booking(date=datetime(2017, 1, 3, 19), user="max")

        with self.assertRaisesRegexp(ValidationError, 'Time must be within business hours from 8 AM and 6 PM'):
            too_early.clean()

        with self.assertRaisesRegexp(ValidationError, 'Time must be within business hours from 8 AM and 6 PM'):
            too_late.clean()

    def test_do_not_allow_to_save_twice_same_user(self):
        date = datetime(2017, 1, 1, 12)
        user = "horst"

        with self.assertRaises(IntegrityError):
            Booking(date=date, user=user, facility='g').save()
            Booking(date=date, user=user, facility='g').save()

    def test_do_not_allow_to_save_twice_different_user(self):
        date = datetime(2017, 1, 1, 12)

        with self.assertRaises(IntegrityError):
            Booking(date=date, user="stefanie", facility='g').save()
            Booking(date=date, user="elena", facility='g').save()

    def test_do_not_allow_to_exceed_quota(self):
        """
        A user should not be able to exceed the quota (regardless of facility)
        """
        date = datetime(2030, 3, 22, 8)
        user = "max"

        Booking(date=date, user=user, facility='g').save()
        Booking(date=date + timedelta(hours=1), user=user, facility='g').save()
        Booking(date=date + timedelta(hours=2), user=user, facility='g').save()
        Booking(date=date + timedelta(hours=3), user=user, facility='h').save()
        Booking(date=date + timedelta(hours=4), user=user, facility='h').save()
        Booking(date=date + timedelta(hours=5), user=user, facility='h').save()
        Booking(date=date + timedelta(hours=6), user=user, facility='g').save()
        Booking(date=date + timedelta(hours=7), user=user, facility='g').save()
        Booking(date=date + timedelta(hours=8), user=user, facility='x').save()
        Booking(date=date + timedelta(hours=9), user=user, facility='y').save()

        with self.assertRaises(ValidationError):
            Booking(date=date + timedelta(days=1),
                    user=user, facility='h').save()

        with self.assertRaises(ValidationError):
            Booking(date=date + timedelta(days=1),
                    user=user, facility='g').save()

    def test_bookings_in_same_week_affect_quota(self):
        """
        Bookings in same week shold affect user quota, regardless which day of the week we have
        """
        user = "edna"
        today = datetime(2017, 3, 1, 8)

        one_day_ago = today - timedelta(1)
        two_days_ago = today - timedelta(2)
        tomorrow = today + timedelta(1)

        Booking(date=one_day_ago, user=user, facility='g').save()
        Booking(date=two_days_ago, user=user, facility='g').save()
        Booking(date=tomorrow, user=user, facility='g').save()

        quota = Booking.get_user_quota(user, date=today)

        self.assertEqual(quota, settings.BOOKINGS_QUOTA - 3)

    def test_bookings_in_future_affect_quota(self):
        """
        Bookings in the future should affect user quota
        """
        user = "edna"
        today = datetime(2017, 3, 1, 8)

        one_week_ahead = today + timedelta(7)
        two_weeks_ahead = today + timedelta(14)
        four_weeks_ahead = today + timedelta(28)

        Booking(date=one_week_ahead, user=user, facility='g').save()
        Booking(date=two_weeks_ahead, user=user, facility='g').save()
        Booking(date=four_weeks_ahead, user=user, facility='g').save()

        quota = Booking.get_user_quota(user, date=today)

        self.assertEqual(quota, settings.BOOKINGS_QUOTA - 3)

    def test_bookings_in_past_do_not_affect_quota(self):
        """
        Bookings in last week or older should not affect user quota
        """
        user = "edna"
        today = datetime(2017, 3, 1, 8)

        one_week_ago = today - timedelta(7)
        two_weeks_ago = today - timedelta(14)
        four_weeks_ago = today - timedelta(28)

        Booking(date=one_week_ago, user=user, facility='h').save()
        Booking(date=two_weeks_ago, user=user, facility='h').save()
        Booking(date=four_weeks_ago, user=user, facility='h').save()

        quota = Booking.get_user_quota(user, date=today)

        self.assertEqual(quota, settings.BOOKINGS_QUOTA)

    def test_booking_knows_its_calendar_week(self):
        self.assertEqual(1, Booking(date=datetime(2017, 1, 2),
                                    user='max', facility='g').calendar_week())
        self.assertEqual(1, Booking(date=datetime(2017, 1, 3),
                                    user='max', facility='g').calendar_week())
        self.assertEqual(1, Booking(date=datetime(2017, 1, 4),
                                    user='max', facility='g').calendar_week())
        self.assertEqual(1, Booking(date=datetime(2017, 1, 5),
                                    user='max', facility='g').calendar_week())
        self.assertEqual(1, Booking(date=datetime(2017, 1, 6),
                                    user='max', facility='g').calendar_week())

        self.assertEqual(10, Booking(date=datetime(2017, 3, 6),
                                     user='max', facility='g').calendar_week())
        self.assertEqual(10, Booking(date=datetime(2017, 3, 7),
                                     user='max', facility='g').calendar_week())
        self.assertEqual(10, Booking(date=datetime(2017, 3, 8),
                                     user='max', facility='g').calendar_week())
        self.assertEqual(10, Booking(date=datetime(2017, 3, 9),
                                     user='max', facility='g').calendar_week())
        self.assertEqual(10, Booking(date=datetime(2017, 3, 10),
                                     user='max', facility='g').calendar_week())

        self.assertEqual(52, Booking(date=datetime(2017, 12, 25),
                                     user='max', facility='g').calendar_week())
        self.assertEqual(52, Booking(date=datetime(2017, 12, 26),
                                     user='max', facility='g').calendar_week())
        self.assertEqual(52, Booking(date=datetime(2017, 12, 27),
                                     user='max', facility='g').calendar_week())
        self.assertEqual(52, Booking(date=datetime(2017, 12, 28),
                                     user='max', facility='g').calendar_week())
        self.assertEqual(52, Booking(date=datetime(2017, 12, 29),
                                     user='max', facility='g').calendar_week())

    def test_booking_knows_whether_it_lies_in_the_past(self):
        """
        A booking knows whether it is a past booking 
        (which is also true if it is a booking running right now, 
        e.g. 10:23:22 is a 10:00 booking and also considered a past booking.)
        """
        now = datetime.now()

        current_date = now.replace(minute=0, second=0, microsecond=0)
        past_date = current_date - timedelta(hours=1)
        future_date = current_date + timedelta(hours=1)

        past = Booking(date=past_date, user='daniel', facility='g')
        current = Booking(date=current_date, user='daniel', facility='g')
        future = Booking(date=future_date, user='daniel', facility='g')

        self.assertTrue(current.lies_in_past())
        self.assertTrue(past.lies_in_past())
        self.assertFalse(future.lies_in_past())
