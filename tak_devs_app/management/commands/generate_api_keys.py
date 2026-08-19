from django.core.management.base import BaseCommand
from rest_framework_api_key.models import APIKey

class Command(BaseCommand):
    help = 'Generate a DRF API key and display its value once'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            default='tak-portfolio-production',
            help='A descriptive name shown in Django admin',
        )

    def handle(self, *args, **options):
        _, key = APIKey.objects.create_key(name=options['name'])
        self.stdout.write(self.style.SUCCESS('API key created. Copy it now; it will not be shown again:'))
        self.stdout.write(key)
