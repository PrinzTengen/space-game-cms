"""Publish the editable footer behind {% static_alias "footer" %} in DE and EN."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from space_game.theme.footer import install_footer


class Command(BaseCommand):
    help = "Install the static footer alias with its default links (DE and EN)."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        user = (
            get_user_model()
            .objects.filter(
                username=options["username"],
                is_superuser=True,
                is_active=True,
            )
            .first()
        )
        if user is None:
            msg = "Pass an existing active superuser with --username."
            raise CommandError(msg)
        changed = install_footer(user)
        self.stdout.write(
            self.style.SUCCESS(f"Installed the footer in {changed} language(s)."),
        )
