from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from space_game.control.models import Upload


class Command(BaseCommand):
    help = "Remove unfinished MCP uploads older than 24 hours."

    def handle(self, *args, **options):
        count, _ = Upload.objects.filter(
            created__lt=timezone.now() - timedelta(hours=24),
        ).delete()
        self.stdout.write(f"Removed {count} expired upload(s).")
