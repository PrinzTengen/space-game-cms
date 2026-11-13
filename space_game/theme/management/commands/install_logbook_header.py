"""Version-safe conversion of the Stories page header into a frontend plugin."""

from cms.models import PageContent
from cms.utils.placeholder import rescan_placeholders_for_obj
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from djangocms_versioning.models import Version

from space_game.theme.install import unchanged_frontend_draft
from space_game.theme.logbook import add_default_logbook_header


class Command(BaseCommand):
    help = "Install an editable Logbook header on each published Stories page."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)

    @transaction.atomic
    def handle(self, *args, **options):
        user = (
            get_user_model()
            .objects.filter(
                username=options["username"],
                is_active=True,
                is_superuser=True,
            )
            .first()
        )
        if user is None:
            msg = "Pass an existing active superuser with --username."
            raise CommandError(msg)
        changed = 0
        for content in PageContent.objects.filter(
            page__reverse_id="stories",
            page__site_id=settings.SITE_ID,
        ):
            header = content.placeholders.filter(slot="logbook_header").first()
            if (
                content.template == "cms/logbook.html"
                and header
                and header.get_plugins()
                .filter(
                    plugin_type="SpaceGameLogbookHeaderPlugin",
                )
                .exists()
            ):
                continue
            draft = PageContent.admin_manager.filter(
                page=content.page,
                language=content.language,
                versions__state="draft",
            ).first()
            if draft and not unchanged_frontend_draft(content, draft):
                msg = f"Logbook ({content.language}) has an unpublished edited draft."
                raise CommandError(msg)
            version = (
                Version.objects.get_for_content(draft)
                if draft
                else Version.objects.get_for_content(content).copy(user)
            )
            draft_content = version.content
            draft_content.template = "cms/logbook.html"
            draft_content.save(update_fields=["template"])
            placeholder = rescan_placeholders_for_obj(draft_content)["logbook_header"]
            if not placeholder.get_plugins().exists():
                add_default_logbook_header(draft_content)
            version.publish(user)
            changed += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Installed editable Logbook header on {changed} page(s).",
            ),
        )
