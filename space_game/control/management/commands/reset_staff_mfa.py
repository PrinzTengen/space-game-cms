"""Server-side recovery when an administrator loses both phone and backup codes."""

from allauth.mfa.models import Authenticator
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone

from space_game.control.models import AuditEvent
from space_game.control.signals import revoke_management_tokens


class Command(BaseCommand):
    help = "Reset staff MFA and revoke sessions and MCP tokens. Requires server access."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        user = (
            get_user_model()
            .objects.filter(username=options["username"], is_staff=True)
            .first()
        )
        if user is None:
            msg = "No such staff account."
            raise CommandError(msg)
        Authenticator.objects.filter(user=user).delete()
        revoke_management_tokens(user.pk)
        for session in Session.objects.filter(
            expire_date__gt=timezone.now(),
        ).iterator():
            if session.get_decoded().get("_auth_user_id") == str(user.pk):
                session.delete()
        AuditEvent.objects.create(
            actor=user,
            tool="server.reset_staff_mfa",
            target=str(user.pk),
        )
        self.stdout.write(
            self.style.SUCCESS(
                "MFA reset. New enrollment is required at the next login.",
            ),
        )
