from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import secrets

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate API keys for users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            if not user.api_key:
                user.api_key = secrets.token_hex(20)
                user.save()
