from django.core.management.base import BaseCommand, CommandError
from website.models import Booking


class Command(BaseCommand):
    help = 'Remove bookings older than n days. Can be configured by setting.OLD_BOOKINGS_EXPIRATION_IN_DAYS.'

    def handle(self, *args, **options):
        removed_bookings = Booking.remove_old()
        self.stdout.write(self.style.SUCCESS(
            'Removed {0} bookings'.format(removed_bookings)))
