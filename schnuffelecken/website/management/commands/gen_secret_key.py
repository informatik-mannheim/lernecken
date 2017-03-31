from django.core.management.base import BaseCommand, CommandError
from django.utils.crypto import get_random_string

class Command(BaseCommand):
    help = 'Generate a new secret key'

    def handle(self, *args, **options):
        self.stdout.write(get_random_string(50))