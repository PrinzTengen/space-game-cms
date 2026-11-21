"""Convert stored component links without changing CMS publication states."""

from django.core.management.base import BaseCommand
from django.db import transaction
from djangocms_frontend.models import FrontendUIItem

from space_game.theme.buttons import BUTTON_FIELDS
from space_game.theme.buttons import convert_buttons


class Command(BaseCommand):
    help = "Convert legacy component buttons to native TextLinkPlugin children."

    @transaction.atomic
    def handle(self, *args, **options):
        count = 0
        for instance in FrontendUIItem.objects.filter(plugin_type__in=BUTTON_FIELDS):
            if any(
                label in instance.config
                for label, _, _ in BUTTON_FIELDS[instance.plugin_type]
            ) or (
                instance.plugin_type == "SpaceGameLauncherPlatformPlugin"
                and not instance.config.get("native_button")
            ):
                convert_buttons(instance)
                count += 1
        self.stdout.write(
            self.style.SUCCESS(f"Converted buttons in {count} components."),
        )
