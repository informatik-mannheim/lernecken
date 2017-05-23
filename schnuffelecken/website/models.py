from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

from datetime import datetime, timedelta

from website.viewmodels import *


class Statistic(models.Model):
    """Simple accumulation of bookings.
    To be extended if more complex statistics are needed.
    """
    calendar_week = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    bookings = models.PositiveSmallIntegerField(default=0)
    facility = models.CharField(max_length=20)

    class Meta:
        unique_together = ("calendar_week", "year", "facility")

    @staticmethod
    def accumulate(bookings):
        """
        Accumulate bookings per calender_week, year and facility.
        """
        for booking in bookings:
            s, _ = Statistic.objects.get_or_create(
                calendar_week=booking.calendar_week(),
                year=booking.date.year,
                facility=booking.facility)

            s.bookings += 1

            s.save()

    def clean(self):
        """
        Validate facility field
        """
        if not self.facility:
            raise ValidationError(
                {'facility': 'Facility must contain a value'})

    def save(self, *args, **kwargs):
        """
        Override default save method to ALWAYS perform a clean()
        to ensure all validation criteria are satisfied.
        """
        self.clean()
        return super(Statistic, self).save(*args, **kwargs)

    def __str__(self):
        return "[{0}][facility:{1}] KW {2}: {3} bookings".format(
            self.year,
            self.facility,
            self.calendar_week,
            self.bookings)


class Booking(models.Model):
    """
    Models a booking. Right now, a booking is very simple - it stores
    the user and facility as just plain strings. The date needs to be
    the exact time the booking starts (e.g. 2017-02-01T09:00:00).
    """
    user = models.CharField(max_length=20)
    facility = models.CharField(max_length=20)
    date = models.DateTimeField()

    class Meta:
        unique_together = ("date", "facility")

    def belongs_to(self, user):
        return user and self.user == user.username

    def calendar_week(self):
        """Return calendar week.
        Note that for example 2017-1-1 is calendar week 52 / 2016!
        But that doesn't matter too much as we only deal with workdays.
        """
        return self.date.isocalendar()[1]

    def lies_in_past(self):
        """
        Check whether a booking lies in the past (hour-wise)
        """
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        return self.date <= now

    @staticmethod
    def get_user_quota(username, date=None):
        """Check user quota (number of available bookings
        from start of current BookingPeriod on).
        """
        date = date or datetime.now()

        threshold = BookingPeriod(date).start

        bookings = Booking.objects.filter(user=username, date__gte=threshold)

        return settings.BOOKINGS_QUOTA - len(bookings)

    @staticmethod
    def remove_old():
        """Remove all entries older than settings.OLD_BOOKINGS_EXPIRATION_IN_DAYS days
        """
        threshold = datetime.now() - timedelta(settings.OLD_BOOKINGS_EXPIRATION_IN_DAYS + 1)
        bookings = Booking.objects.filter(date__lte=threshold)
        removed_bookings = 0

        with transaction.atomic():
            removed_bookings = len(bookings)
            Statistic.accumulate(bookings)
            bookings.delete()

        return removed_bookings

    def save(self, *args, **kwargs):
        """
        Override default save method to ALWAYS perform a clean()
        to ensure all validation criteria are satisfied.
        """
        self.clean()
        return super(Booking, self).save(*args, **kwargs)

    def clean(self):
        """
        Validate date and quota
        """
        if self.date.minute or self.date.second:
            raise ValidationError(
                {'time': 'Time must contain only full hours'})
        if self.date.hour < 8 or self.date.hour > 18:
            raise ValidationError(
                {'time': 'Time must be within business hours from 8 AM and 6 PM'})
        if Booking.get_user_quota(self.user) == 0:
            raise ValidationError({'quota': 'No more bookings left'})

    def __str__(self):
        return "{0} ({1})".format(self.user, self.date)


class BookingPeriod(object):
    """Represents one bookable period of four weeks.
    Given a date, it will find the corresponding monday
    (either the last monday if it is a workday or
    the next monday if it is a weekend day).
    """

    def __init__(self, date=None):
        self.num_weeks = 4
        self.start = self._find_start(date or datetime.now())
        self.weeks = self._create_weeks()

    def _find_start(self, date=None):
        today = date or datetime.now()

        if today.weekday() < 5:
            monday = today - timedelta(today.weekday())
        else:
            monday = today + timedelta(7 - today.weekday())

        return monday.replace(hour=0, minute=0, second=0, microsecond=0)

    def _create_weeks(self):
        return [Week(self.start + timedelta(i * 7)) for i in range(0, self.num_weeks)]

    def __str__(self):
        return str(self.start)


class Week(object):
    """
    Represents a week with five days, always starting on a monday.
    Just a simple container for Day instances that also knows the
    calendar week.
    """

    def __init__(self, start):
        self.start = start
        self.days = [Day(self.start + timedelta(i)) for i in range(0, 5)]
        self.calendar_week = self.start.isocalendar()[1]


class Day(object):
    """Represents one day and the corresponding bookings
    as either booked, reserved or available.
    """

    def __init__(self, date):
        self.date = date
        self.bookings = []

    def get_bookings(self, facility, user):
        """
        To reduce database queries, it will lazily fetch the bookings on
        first call and cache them. If for future usage it should also reflect
        the latest DB state, this needs to be changed
        (probably needs some refactoring then).
        """
        if not self.bookings:
            start_time = 8
            end_time = 19

            query_set = Booking.objects.filter(
                facility=facility, date__date=self.date)

            for i in range(start_time, end_time):
                slot = datetime(
                    self.date.year, self.date.month, self.date.day, i)

                if len(list(filter(lambda b: b.date == slot and b.user == user.username, query_set))) == 1:
                    self.bookings.append(BlockReserved(slot))
                elif len(list(filter(lambda b: b.date == slot, query_set))) == 1:
                    self.bookings.append(BlockBooked(slot))
                else:
                    self.bookings.append(BlockAvailable(slot))

        return self.bookings
