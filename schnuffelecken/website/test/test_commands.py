from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO

from datetime import datetime, timedelta
from website.models import Booking


class CommandsTests(TestCase):

    def setUp(self):
        now = datetime.now()
        self.today = datetime(
            year=now.year, month=now.month, day=now.day, hour=8)

    def test_gen_secret_key(self):
        """
        Test generation of secret keys (as good as it gets)
        """
        args = []
        opts = {}
        out = StringIO()

        call_command('gen_secret_key', *args, **opts, stdout=out)

        result = out.getvalue()

        self.assertEqual(len(result.strip()), 50)

    def test_remove_old_bookings(self):
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

        args = []
        opts = {}
        out = StringIO()

        call_command('remove_old_bookings', *args, **opts, stdout=out)

        result = out.getvalue()

        self.assertIn("Removed 3 bookings", result)
        self.assertEqual(len(Booking.objects.all()), 3)
