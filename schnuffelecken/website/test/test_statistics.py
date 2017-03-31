from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.test.utils import setup_test_environment

from website.models import *

setup_test_environment()


class StatisticTests(TestCase):

    def setUp(self):
        pass

    def test_can_save_and_retrieve_statistic(self):
        s = Statistic(year=2017, calendar_week=52,
                      facility='g', bookings=0)
        s.save()

        self.assertEqual(Statistic.objects.first(), s)

    def test_enforces_unique_check(self):
        """
        A statistic is a unique combination of calendar_week, facility and year
        """
        s1 = Statistic(year=2017, calendar_week=52, facility='g', bookings=0)
        s2 = Statistic(year=2017, calendar_week=52, facility='g', bookings=3)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                s1.save()
                s2.save()

        self.assertEqual(Statistic.objects.count(), 0)

    def test_can_save_different_statistics(self):
        """
        Test if persistence works
        """
        Statistic(year=2017, calendar_week=52, facility='g', bookings=0).save()
        Statistic(year=2017, calendar_week=52, facility='f', bookings=3).save()
        Statistic(year=2017, calendar_week=50, facility='g', bookings=3).save()
        Statistic(year=2016, calendar_week=1, facility='x', bookings=3).save()

        self.assertEqual(Statistic.objects.count(), 4)

    def test_calendar_week_can_not_be_empty(self):
        """
        Calender week can not be empty
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Statistic(year=2017, facility='g', bookings=0).save()

    def test_year_can_not_be_empty(self):
        """
        Year can not be empty
        """
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Statistic(calendar_week=7, facility='g', bookings=0).save()

    def test_facility_can_not_be_empty(self):
        """
        Facility can not be empty
        """
        with self.assertRaises(ValidationError):
            Statistic(calendar_week=7, year=2017, bookings=0).save()

    def test_accumulate_bookings_for_same_facility_and_kw(self):
        """
        Accumulate bookings from one calendar week into one statistics row
        """
        kw9 = [
            Booking(date=datetime(2017, 2, 27, 11),
                    user="horst", facility="g"),
            Booking(date=datetime(2017, 2, 28, 11), user="max", facility="g",),
            Booking(date=datetime(2017, 3, 1, 11), user="klaus", facility="g"),
            Booking(date=datetime(2017, 3, 2, 11),
                    user="stefan", facility="g"),
            Booking(date=datetime(2017, 3, 3, 11), user="maria", facility="g"),
            Booking(date=datetime(2017, 3, 3, 12), user="maria", facility="g")
        ]

        Statistic.accumulate(kw9)

        self.assertEqual(1, Statistic.objects.count())

        s_kw9 = Statistic.objects.get(year=2017, calendar_week=9, facility='g')

        self.assertEqual(s_kw9.bookings, 6)

    def test_handle_bookings_different_facilities_and_kws(self):
        """
        Accumulate bookings from one calendar week 
        and two facilities into two statistics rows
        """
        kw10 = [
            Booking(date=datetime(2017, 3, 6, 8), user="horst", facility="h"),
            Booking(date=datetime(2017, 3, 7, 9), user="horst", facility="h"),
            Booking(date=datetime(2017, 3, 8, 10), user="horst", facility="h"),
            Booking(date=datetime(2017, 3, 9, 11), user="horst", facility="g"),
            Booking(date=datetime(2017, 3, 10, 12), user="horst", facility="g")

        ]

        Statistic.accumulate(kw10)

        self.assertEqual(2, Statistic.objects.count())

        kw_10_g = Statistic.objects.get(
            year=2017, calendar_week=10, facility='g')
        kw_10_h = Statistic.objects.get(
            year=2017, calendar_week=10, facility='h')

        self.assertEqual(kw_10_g.bookings, 2)
        self.assertEqual(kw_10_h.bookings, 3)

    def test_handle_bookings_different_facilities_and_kws_and_years(self):
        """
        Accumulate diverse bookings into separate statistics rows
        """
        kw10_2017_h = Booking(date=datetime(2017, 3, 6, 8),
                              user="horst", facility="h")
        kw10_2018_h = Booking(date=datetime(
            2018, 3, 5, 18), user="horst", facility="h")
        kw10_2018_g = Booking(date=datetime(
            2018, 3, 5, 18), user="horst", facility="g")

        Statistic.accumulate([kw10_2017_h, kw10_2018_h, kw10_2018_g])

        self.assertEqual(3, Statistic.objects.count())

        self.assertEqual(Statistic.objects.get(
            year=2017, calendar_week=10, facility='h').bookings, 1)
        self.assertEqual(Statistic.objects.get(
            year=2018, calendar_week=10, facility='h').bookings, 1)
        self.assertEqual(Statistic.objects.get(
            year=2018, calendar_week=10, facility='g').bookings, 1)
